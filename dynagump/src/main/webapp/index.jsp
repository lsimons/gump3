<html>
<head>
 <title>Apache Gump 3.0</title>
 <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
 <link rel="stylesheet" type="text/css" href="resources/styles/print.css" media="print"/>
 <link rel="stylesheet" type="text/css" href="resources/styles/base/content.css" media="all"/>
 <link rel="stylesheet" type="text/css" href="resources/styles/cavendish/content.css" title="Cavendish" media="all"/>
 <link rel="stylesheet" type="text/css" href="resources/styles/base/template.css" media="screen"/>
 <link rel="stylesheet" type="text/css" href="resources/styles/cavendish/template.css" title="Cavendish" media="screen"/>
 <link rel="icon" href="resources/images/icon.png" type="image/png"/>
 <script src="resources/scripts/search.js" type="text/javascript">//</script>
</head>

<body>

<div id="top">
 <ul class="path">
   <li class="current">Home</li>
  </ul>
</div>

<div id="center">

<div id="header">
 <h1><a href="./" title="Apache Gump" accesskey="1">Apache Gump</a></h1>
 <ul>
  <li><a href="./results/" title="Results">Results</a></li>
  <li class="current"><span>Home</span></li>
 </ul>
 <div class="searchbox">
   <label> </label>
   <!--input type="text" width="10" onkeyup="act(event)"/-->
 </div>
</div>

<div id="body">

 <h1>Welcome to Apache Gump!</h1>

 <p>Gump is Apache's continuous integration tool. It is written in python
and fully supports Apache Ant, Apache Maven and other build tools. Gump
is unique in that it builds and compiles software against the latest
development versions of those projects. This allows gump to detect
potentially incompatible changes to that software just a few hours
after those changes are checked into the version control system.
Notifications are sent to the project team as soon as such a change is
detected, referencing more detailed reports available online.</p>

 <p>You can set up and run Gump on your own machine and run it on your own
projects, however it is currently most famous for building most of
Apache's java-based projects and their dependencies (which constitutes
several million lines of code split up into hundreds of projects). For
this purpose, the gump project maintains its own dedicated server.</p>

 <h2>Build results</h2>

 <p>Apache dedicates a complete machine to running gump. The 
<a href="results/">Build results</a> page provides a view of the data
gump generates for apache.</p>

</div>

</div>

<%@ include file="bottom.inc" %>

</body>
</html>  







