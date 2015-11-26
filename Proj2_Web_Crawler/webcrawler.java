import java.io.*;
import java.net.*;
import java.util.*;
import java.util.zip.GZIPInputStream;
import org.jsoup.*;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;       
import org.jsoup.nodes.Element;


public class webcrawler {

	static Socket client = null;
	static BufferedReader ipMsg = null, zipMsg = null;
	static PrintWriter out = null;
	static InputStreamReader isr = null;
	static HashSet<String> allLinks = new HashSet<String>();
	static LinkedList<String> queue = new LinkedList<String>();
	static LinkedList<String> secret_flags = new LinkedList<String>();
	static String sessionid = null;
	static String host = "cs5700f14.ccs.neu.edu";
	static boolean is_500 = false, is_closed = false; 
	public static void main(String args[]) throws IOException
	{
		String username = null, password = null;
		String HTTPmsg = null, CRLF = "\r\n", message, htmlpage = null, next_link = null;
		String[] get_reply= null;
		int port = 80;
		boolean found_all_flags = false;
		String loginLink = "/accounts/login/?next=/fakebook/";

		username = args[0];
		password = args[1];

		try
		{
			InetAddress inet = InetAddress.getByName(host);
			client = new Socket(inet , port);

			out = new PrintWriter(client.getOutputStream(), true);

			isr = new InputStreamReader(client.getInputStream());
			ipMsg = new BufferedReader(isr);

			get_reply = makeHTTPConnection(loginLink, username, password);

			if(get_reply != null)
			{
				sessionid = get_reply[0];
				next_link = get_reply[1];
				allLinks.add(next_link);
				queue.add(next_link);

				while(!queue.isEmpty())
				{
					next_link = queue.pop();
					found_all_flags = crawl_page(next_link);

					if (found_all_flags)
						break;
				}
			}
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		finally
		{
			if (client != null)
				client.close();
		}
	}

	static boolean crawl_page (String page_link) throws IOException
	{
		/*
		 *	1. Create HTTP GET request for input link which is relative link.
		 *	2. Send request to server.
		 *	3. Read server response header using inMsg.readLine() and verify
		 *	   response code.
		 *		a. Call error code handling function.
		 *		b. If server returned 200, else handle according code.
		 *	4. Retrieve data from server using Content-Length from response header.
		 *	5. Parse HTML page and check for secret flag. If found, store in array.
		 *	6. If all 5 flags found, print and exit code.
		 *	6. Retrieve all links on page and loop through links and extract only 
		 *	   links from cs5700f14.ccs.neu.edu domain.
		 *	7. Check if valid links exist in HashSet. If not, add them to hashSet
		 *	   and to queue.
		 * */
		String message, html = null, HTTPmsg = "", CRLF = "\r\n", flag = null, moved_link = null;
		String[] splitMsg = null;
		Document doc = null;
		int offset = 0, content_length = 0, read_len = 0;
		char[] html_data = null;
		boolean is_chunked = false, is_gzip = false;

		if (is_500 || is_closed || client == null)
		{
			InetAddress inet = InetAddress.getByName(host);
                        client = new Socket(inet , 80);

                        out = new PrintWriter(client.getOutputStream(), true);

                        isr = new InputStreamReader(client.getInputStream());
                        ipMsg = new BufferedReader(isr);

			is_500 = false;	
			is_closed = false;	
		}

		HTTPmsg = "GET " + page_link + " HTTP/1.1" + CRLF;
		HTTPmsg += "Host: " + host + CRLF;	
		HTTPmsg += "Connection: keep-alive" + CRLF;
		HTTPmsg += "Cookie: sessionid=" + sessionid + CRLF + CRLF;

		out.write(HTTPmsg);
		out.flush();

		message = "";
		message = ipMsg.readLine();

		while (!message.contains("HTTP/1.1"))
		{
			message = ipMsg.readLine();
		}
		html += message + "\n";

		splitMsg = message.split(" ");

		if (splitMsg[1].equals("200")) /* Page found. */
		{
			message = ipMsg.readLine();
			while(message.length() != 0)
			{
				if (message.contains("Content-Length"))
				{
					message = message.split(" ")[1];
					content_length = Integer.parseInt(message);
				}
				if (message.equals("Transfer-Encoding: chunked"))
				{
					is_chunked = true;
				}
				if (message.contains("gzip"))
				{
					is_gzip = true;
				}
				if (message.equals("Connection: close"))
				{
					is_closed = true;
				}

				html += message;
				message = ipMsg.readLine();

			}

			if (is_chunked)
			{
				html = crawl_chunked_page ();
			}
			else if (is_gzip)
			{
				zipMsg = new BufferedReader(new InputStreamReader(new GZIPInputStream(client.getInputStream())));
				html = crawl_gzip_page(content_length);
			}
			else
			{
				html_data = new char[content_length];
				read_len = ipMsg.read(html_data, offset, content_length);

				html = new String(html_data);
			}

			doc = Jsoup.parse(html);
			Elements h2_tags = doc.select("h2");

			for (Element h2 : h2_tags)
			{
				if (h2.attr("class").equals("secret_flag")
						&& h2.attr("style").equals("color:red"))
				{
					flag = h2.text();
					flag = flag.substring(6).trim();
					if (!secret_flags.contains(flag))
						secret_flags.add(flag);
					System.out.println(flag);
				}
				if (secret_flags.size() == 5)
					return true;

			}

			Elements links = doc.select("a");

			for (Element link : links)
			{
				String friend_link = link.attr("href");
				if (!allLinks.contains(friend_link) && friend_link.contains("/fakebook/"))
				{
					allLinks.add(friend_link);
					queue.add(friend_link);
				}
			}

		}
		else if (splitMsg[1].equals("301"))     /* Moved to new URL. */
		{
			// Code to move to new link.
			while((message = ipMsg.readLine()) != null)
			{
				if (message.contains("Location: "))
				{
					message = message.split(":")[2].trim();
					moved_link = message.split(host)[1];

					if (!allLinks.contains(moved_link))
					{
						allLinks.add(moved_link);
						return crawl_page(moved_link);
					}
					return false;
				}
			}
		}
		else if (splitMsg[1].equals("403") || splitMsg[1].equals("404")) /* Page not found. */
		{
			return false;
		}
		else if (splitMsg[1].equals("500")) /* Internal Server Error. */
		{
			is_500 = true;
			if (client != null)
			{
				client.close();
			}

			return crawl_page(page_link);
		}

		return false;

	}

	static String crawl_chunked_page () throws IOException
	{
		String message = null, html_page = "",  html = "";
		int chunk_len = 0, remaining_len = 0;
		String[] splitMsg = null;
		Document doc = null;
		int offset = 0, content_length = 0, read_len = 0;
		char[] html_data = null;

		while (true)
		{
			message = ipMsg.readLine();

			if (message == null || message.equals(""))
				continue;

			if (message.equals("0"))
				break;

			message = message.split(";")[0];
			try
			{
				chunk_len = Integer.parseInt(message, 16);
			}
			catch (java.lang.NumberFormatException e)
			{}


			html_data = new char[chunk_len];
			remaining_len = chunk_len;

			while (offset != chunk_len)
			{
				read_len = ipMsg.read(html_data, offset, remaining_len);
				offset += read_len;
				remaining_len -= read_len;
				html_page = new String(html_data);
				html += html_page;
			}

			html_data = null;
			offset = 0;
		}

		return html;

	}

	static String crawl_gzip_page(int content_length) throws IOException
	{
                String message = null, html_page = "",  html = "";
                int chunk_len = 0;
                String[] splitMsg = null;
                Document doc = null;
                int offset = 0, read_len = 0;
                char[] html_data = null;

		html_data = new char[content_length];
		read_len = zipMsg.read(html_data, offset, content_length);


		html_page = new String(html_data);
		return html_page;
	}

	static String[] makeHTTPConnection(String loginLink, String username, String password) throws IOException
	{
		String HTTPmsg = null, message = null, CRLF = "\r\n", html = null;
		String csrftoken = null, sessionid = null, user_field = null, pass_field = null, moved_link = null;
		String csrf_field = null, next_link = null, httpPost = null, action = null, data = null;
		String[] splitMsg = null;
		String[] get_reply= new String[2];
		Document doc = null;
		int offset = 0, content_length = 0, read_len = 0;
		char[] html_data = null;
		boolean is_chunked = false;

		HTTPmsg = "GET " + loginLink + " HTTP/1.1" + CRLF;
		httpPost += "Connection: Keep-alive" + CRLF;
		HTTPmsg += "Host: " + host + ":80" + CRLF + CRLF;


		out.write(HTTPmsg);

		out.flush();

		message = ipMsg.readLine();
		html += message + "\n";

		splitMsg = message.split(" ");

		if (splitMsg[1].equals("200")) /* Page found. */
		{
			message = ipMsg.readLine();
			while(message.length() != 0)
			{
				if (message.contains("csrftoken"))
				{
					message = message.split("=")[1].trim();
					csrftoken = message.split(";")[0];
				}
				else if (message.contains("sessionid"))
				{
					message = message.split("=")[1].trim();
					sessionid = message.split(";")[0];
				}
				else if (message.contains("Content-Length"))
				{
					message = message.split(" ")[1];
					content_length = Integer.parseInt(message);
				}
				if (message.equals("Transfer-Encoding: chunked"))
                                {
                                        is_chunked = true;
                                }
				html += message;
				message = ipMsg.readLine();
			}
			if (is_chunked)
                        {
                                html = crawl_chunked_page ();
                        }
			else
			{
				html_data = new char[content_length];
				read_len = ipMsg.read(html_data, offset, content_length);
			
				html = new String(html_data);
			}
			doc = Jsoup.parse(html);
			Elements inputs = doc.select("input");

			for (Element input : inputs)
			{
				if (input.attr("id").equals("id_username"))
					user_field = input.attr("name");

				if (input.attr("id").equals("id_password"))
					pass_field = input.attr("name");

				if (input.attr("name").equals("csrfmiddlewaretoken"))
					csrf_field = input.attr("name");

				if (input.attr("name").equals("next"))
				{
					next_link = input.attr("value");
					next_link = next_link.replaceAll("/", "%2F");
				}
			}

			Elements forms = doc.select("form");
			for (Element form : forms)
				if (form.attr("method").equals("post"))
					action = form.attr("action");

			data = user_field + "=" + username + "&" + pass_field + "=" + password;
			data += "&" + csrf_field + "=" + csrftoken + "&next=" + next_link;

			httpPost = "POST " + loginLink + " HTTP/1.1" + CRLF;
			httpPost += "Host: cs5700f14.ccs.neu.edu" + CRLF;
			httpPost += "Connection: keep-alive" + CRLF;
			httpPost += "Cookie: csrftoken=" + csrftoken + "; sessionid=" + sessionid + CRLF;
			httpPost += "Content-Type: application/x-www-form-urlencoded" + CRLF;
			httpPost += "Content-Length: " + data.length() + CRLF;
			httpPost += CRLF + data + CRLF + CRLF;

			out.write(httpPost);
			out.flush();

			message = "";
			html = "";
			message = ipMsg.readLine();
                	while (!message.contains("HTTP/1.1"))
                	{
                        	message = ipMsg.readLine();
                	}
			//System.out.println(message);
			splitMsg = message.split(" ");

			if (splitMsg[1].equals("302") || splitMsg[1].equals("303"))
			{
				while(message.length() != 0)
				{
					html += message + "\n";
					if (message.contains("sessionid"))
					{
						message = message.split("=")[1].trim();
						get_reply[0] = message.split(";")[0];
					}

					if (message.contains("Location"))
					{
						message = message.split(":")[2].trim();
						get_reply[1] = message.split("//cs5700f14.ccs.neu.edu")[1].trim();
					}
					message = ipMsg.readLine();
				}
				return get_reply;
			}
			else if (splitMsg[1].equals("200"))
			{
				System.out.println("Please enter valid username and password.");
			}	
		}
		else if (splitMsg[1].equals("301"))	/* Moved to new URL. */
		{
			// Code to move to new link.
			while((message = ipMsg.readLine()) != null)
                        {
                                if (message.contains("Location: "))
                                {
                                        message = message.split(":")[2].trim();
                                        moved_link = message.split(host)[1];
                                        if (!allLinks.contains(moved_link))
                                        {
                                                allLinks.add(moved_link);
                                                return makeHTTPConnection(moved_link, username, password);
                                        }
                                        return get_reply; 
                                }
                        }
		}
		else if (splitMsg[1].equals("403") || splitMsg[1].equals("404")) /* Page not found. */
		{
			return get_reply;
		}
		else if (splitMsg[1].equals("500")) /* Internal Server Error. */
		{
			return makeHTTPConnection(host, username, password);
		}
		return get_reply;
	}

}




