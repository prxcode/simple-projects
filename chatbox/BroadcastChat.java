import java.net.*;
import java.io.*;

public class BroadcastChat {
    public static void main(String[] args) throws IOException {
        DatagramSocket socket = new DatagramSocket(8888);
        socket.setBroadcast(true);

        System.out.println("Broadcast chat started. Type your messages:");

        // Thread to receive messages
        new Thread(() -> {
            byte[] buffer = new byte[1024];
            while (true) {
                try {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);
                    String message = new String(packet.getData(), 0, packet.getLength());
                    System.out.println("Friend: " + message);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();

        // Main thread sends messages
        BufferedReader userInput = new BufferedReader(new InputStreamReader(System.in));
        String msg;
        while ((msg = userInput.readLine()) != null) {
            byte[] data = msg.getBytes();
            DatagramPacket packet = new DatagramPacket(
                data,
                data.length,
                InetAddress.getByName("255.255.255.255"), // broadcast address
                8888
            );
            socket.send(packet);
        }
    }
}
