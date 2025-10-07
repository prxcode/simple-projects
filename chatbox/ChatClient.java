import java.io.*;
import java.net.*;

public class ChatClient {
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("Usage: java ChatClient <server_ip>");
            return;
        }

        String serverIp = args[0];
        Socket socket = new Socket(serverIp, 5000);
        System.out.println("Connected to server: " + serverIp);

        BufferedReader keyboard = new BufferedReader(new InputStreamReader(System.in));
        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

        // Thread to listen for messages from server
        new Thread(() -> {
            try {
                String fromServer;
                while ((fromServer = in.readLine()) != null) {
                    System.out.println("Friend: " + fromServer);
                }
            } catch (IOException e) {
                System.out.println("Disconnected from server.");
            }
        }).start();

        // Read from keyboard and send to server
        String userInput;
        while ((userInput = keyboard.readLine()) != null) {
            out.println(userInput);
        }

        socket.close();
    }
}
