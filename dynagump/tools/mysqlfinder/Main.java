public class Main
{
  public static void main(String[] args) {
    try {
      Class.forName("com.mysql.jdbc.Driver");
      System.exit(0);
    } catch(Throwable t) {
      System.out.println("MySQL Driver not found!");
      System.exit(1);
    }
  }
}
