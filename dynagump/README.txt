



                             D y n a G u m p



  What is this?
  -------------

  DynaGump is a web application to present gump data.
  

  Requirements
  ------------
  
  DynaGump is a java web application and requires a Java 1.4 or greater
  compatible JVM.
  
  
  How do I start it?
  ------------------

  1) you need mysql 4.x or later installed.
  2) you need the mysql JDBC drivers installed and visibile (either in the classpath
  or in the webapp/WEB-INF/lib directory) 
  3) open webapp/WEB-INF/cocoon.xconf and modify the <dburl> tag according to your setup
  4) import the testing database dump that you find in src/sql/mysql.dump
  5) run ./dynagump.sh run
  6) point your browser to http://localhost:8080/

  That's it!
  
  
  What is this cocoon thing?
  --------------------------
  Cocoon is, mildly put, a rather big project to get to grips with. You can
  easily spend a week or two reading all its documentation (at
  http://cocoon.apache.org/). However, you don't need to. Our cocoon setup is
  a java web application that has its logic contained in the xml files inside
  the webapp/ directories. When the webapp is running, edits to those xml files
  will immediately have an effect.
  
  Just a few concepts to get to grips with:
  
  * sitemap. The file webapp/sitemap.xmap "wires up" all the different parts
    that make up cocoon. It's important. Don't worry about most of it for now.
    The key bit you do need to worry about a little is the <map:pipeline>
    element, which defines how the various XML and XSP pages (see below) and other
    resources are offered through the webapp.
    
  * config. The file webapp/WEB-INF/cocoon.xconf configures all those
    different parts after they're wired up. It's important. For now the only
    bit you need to worry about is that <dburl/> configuration mentioned
    above.

  * xml server pages. XSP is the technology used by cocoon instead of something
    like Java Server Pages  and taglibs. We embed java code inside the XSP page.
    Use <xsp:logic></xsp:logic> to embed java code in the page, and
    <xsp:expr></xsp:expr> to include the output of that code on the page itself.
    Simple enough.
    
    See http://cocoon.apache.org/2.1/userdocs/xsp/logicsheet-concepts.html#XSLT+Logicsheets+and+XSP+for+Java

  * esql. ESQL is an XML-based "minilanguage" that we use as a part of XSP pages
    for working with SQL databases. With a connection pool and the like set up
    via the sitemap and config files, we can fire of SQL queries and iterate over
    the results easily enough.
    
    See http://cocoon.apache.org/2.1/userdocs/xsp/esql.html

  * xslt. That's the W3C-standard XSLT language, which transforms one kind of
    XML into another. We have some XSLT pages in webapp/stylesheets which the
    sitemap links to our XML and XSP pages to generate HTML output.

  * the database model. The mysql dump you imported contains a very dense
    summary of a lot of complex gump topics. Some docs are in progress,
    currently at
    
    https://svn.apache.org/repos/asf/gump/trunk/src/xdocs
    
    but it ain't a lot just yet.
  
  
  Uh, ok. So how can I contribute here?
  -------------------------------------
  Let's say you've figured out a piece of info that needs to be extracted from
  the database. The development process is somewhat like this:
  
  1) fire up the web application and mysql server if neccessary
  2) take a look through your web browser to ensure things are in working order
  3) write a query and test it using your favorite mysql client.
  4) copy an existing .xsp page (for example results/builds.xsp) to a new file
  5) edit the style and sidebar info for your new page
  6) edit the <content> part of the page, writing some XSP logic and some ESQL
     to execute your query and format the results.
  7) if neccessary, create or modify a sitemap.xmap based on one of the existing
     sitemap files.
  8) refresh your browser page and visit your newly created page
  9) re-iterated over these steps until it works ;)
  10) svn commit your new xsp file.
  
  Once again, your really don't need to understand all of cocoon to be
  productive in this way! Just a little XML knowledge, enough SQL, a good grip
  on how gump works and a little stubborness is all you need :-D.

                                 --- o ---



  Thanks for your interest.




                                                      The Apache Gump Project
                                                      http://gump.apache.org/

