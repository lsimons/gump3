import java.io.FileInputStream;
import java.io.BufferedInputStream;

public class Main2
{
  public static void main(String[] args) throws Exception {
    System.out.println("  Main2 line 4");
    System.err.println("  Main2 line 5 (to stderr)");

    System.out.println("  Main2 changing input...");
    FileInputStream input = new FileInputStream("Main2.java");
    System.setIn(input);
    System.gc();
    
    processInput();
    System.err.println("  Main2 is done processing...");
    System.gc();
    System.err.println("  Going to sleep for a bit...");
    Thread.sleep(2000);
    System.err.println("  Woke up!");
      }
  
  public static void processInput() throws Exception
  {
    BufferedInputStream input = new BufferedInputStream(System.in);
    System.err.println("Echoing Main2.java");
    while(true)
    {
      int b = input.read();
      if( b == -1 )
      {
        return;
      }
      System.out.write(b);
    }
  }
}
