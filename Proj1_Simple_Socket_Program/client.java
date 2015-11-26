import java.io.BufferedReader;
import java.io.*;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.*;
import java.net.Socket;
import javax.net.ssl.*;
import java.io.BufferedOutputStream;
import java.net.InetAddress;

class client 
{
    public static void main(String args[]) throws IOException
    {
                int port = 27993, i = 0;
                String host = "", nuid = "", message = "";
                String splitMsg[];
		SSLSocketFactory sslfactory;
		SSLSocket sslclient = null;
                Socket client = null;
                int operand1 = 0, operand2 = 0, solution = 0;
                char operator = 0;
		boolean is_ssl = false;
		PrintWriter out = null;
		BufferedReader ipMsg = null;

                System.out.println(args[0] + args[1]);

                if (args.length == 2)
                {
                        host = args[0];
                        nuid = args[1];
                }
                else if (args.length == 3 && args[0].equals("-s"))
                {
                        // Connect using SSL
			is_ssl = true;
			port = 27994;
                        host = args[1];
                        nuid = args[2];
                }
                else if (args.length == 4 && args[0].equals("-p"))
                {
                        port = Integer.parseInt(args[1]);
                        host = args[2];
                        nuid = args[3];
                }
                else if (args.length == 5 && args[0].equals("-p") && args[2].equals("-s"))
                {
                        port = Integer.parseInt(args[1]);
                        host = args[3];
                        nuid = args[4];
                }
                else
                {
                        System.out.println("Incorrect Usage.");
                        System.exit(0);
                }

                try {
                        InetAddress inet = InetAddress.getByName(host);
			System.out.println("1");
			System.out.println(host + port);
			if(!is_ssl)
                        {
				client = new Socket(inet , port);

				System.out.println("2");
                        	OutputStreamWriter osw = new OutputStreamWriter(client.getOutputStream());
                        	BufferedWriter opMsg = new BufferedWriter(osw);

				out = new PrintWriter(client.getOutputStream(), true);


				System.out.println("3");
                        	InputStreamReader isr = new InputStreamReader(client.getInputStream());
                        	ipMsg = new BufferedReader(isr);

                        	//opMsg.write("cs5700fall2014 HELLO " + nuid + "\n");
			}
			else
			{
				System.out.println("4");
				sslfactory = (SSLSocketFactory)SSLSocketFactory.getDefault();
				sslclient = (SSLSocket)sslfactory.createSocket(inet , port);
				System.out.println("5");
				socketInfo(sslclient);
				sslclient.startHandshake();
				System.out.println("6");

				out = new PrintWriter(sslclient.getOutputStream(), true);

				InputStreamReader isr = new InputStreamReader(sslclient.getInputStream());
				ipMsg = new BufferedReader(isr);
			}

                        out.println("cs5700fall2014 HELLO " + nuid);
			System.out.println("6");

                        while (true)
                        {
				System.out.println("inside while");
				i++;
                                message = ipMsg.readLine();
				System.out.println("after readLine");
                                splitMsg = message.split(" ");

				if (message.length() > 256)
					break;

                                if (splitMsg[2].equals("BYE"))
                                {
                                        System.out.println("Secret flag is " + splitMsg[1]);
                                        break;
                                }
                                else if (splitMsg[1].equals("STATUS"))
                                {
			                System.out.println("status");
                                        operand1 = Integer.parseInt(splitMsg[2]);
                                        operand2 = Integer.parseInt(splitMsg[4]);
                                        operator = splitMsg[3].toCharArray()[0];

                                        switch (operator)
                                        {
                                                case '+' : solution = operand1 + operand2;
                                                                   break;
                                                case '-' : solution = operand1 - operand2;
                                                                   break;
                                                case '*' : solution = operand1 * operand2;
                                                                   break;
                                                case '/' : solution = operand1 / operand2;
                                                                   break;
                                                case '%' : solution = operand1 % operand2;
                                                                   break;
                                                case '^' : solution = (int) Math.pow(operand1, operand2);
                                                                   break;
                                        }

                                        //opMsg.write("cs5700fall2014 " + solution + "\n");
                                        out.println("cs5700fall2014 " + solution);
			        	System.out.println(i + ". " + message + " = " + solution);
                                }
                        }

                } catch (UnknownHostException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                }
                finally {
                        try {
                                client.close();
                                System.out.println("Done");
                        }
                        catch  (UnknownHostException e) {
                                // TODO Auto-generated catch block
                                e.printStackTrace();
                        }
                }
        }

	private static void socketInfo(SSLSocket s) {

	System.out.println("Socket class: "+s.getClass());
     System.out.println("   Remote address = "
        +s.getInetAddress().toString());
     System.out.println("   Remote port = "+s.getPort());
     System.out.println("   Local socket address = "
        +s.getLocalSocketAddress().toString());
     System.out.println("   Local address = "
        +s.getLocalAddress().toString());
     System.out.println("   Local port = "+s.getLocalPort());
     System.out.println("   Need client authentication = "
        +s.getNeedClientAuth());
     SSLSession ss = s.getSession();
     System.out.println("   Cipher suite = "+ss.getCipherSuite());
     System.out.println("   Protocol = "+ss.getProtocol());
	

       }

}

