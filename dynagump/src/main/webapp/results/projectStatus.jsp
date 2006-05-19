<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>

<div id="top">
 <ul class="path">
  <li><a href="../index.jsp" title="Home">Home</a></li>
  <li><a href="./" title="Results">Results</a></li>
  <li><a href="Workspaces.gump" title="By Builds">By Builds</a></li>
  <li><a href="ShowRuns.gump?workspace=<bean:write name="currentWorkspace"/>" title="Select Run">Select Run</a></li>
  <li><a href="StatusRun.gump?id=<bean:write name="currentRun"/>" title="Results for this run">Build Results</a></li>
  <li class="current"><bean:write name="project" property="projectName"/></li>
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>

<div id="body">

    <h1>Package <bean:write name="project" property="projectName"/></h1>

    	<h3>description</h3>
    	<p><bean:write name="project" property="description"/></p>
		
	<h3>State</h3>
	<ul>
		<li>Current State: <bean:write name="project" property="resultString"/></li>
		<li>Reason: </li>
 		<li>Start Time: <bean:write name="project" property="startTime" /></li>
 		<li>End Time: <bean:write name="project" property="endTime" /></li>
	</ul>

 	<h3>Log</h3>

 	<p><bean:write name="project" property="log"/></p>

 	<h3>Details</h3>
 	<ul>
 		<li>Containing Module: <bean:write name="project" property="module" /></li>
 		<li>Classpath: Not Implemented.</li>
 	</ul>

 	<h3>Dependencies</h3>

	 	<p>
	 	This package depends on:
	 	<ul>												
	 	<logic:iterate id="depends" name="project" property="dependantList">
	 		<li><a href="ProjectStatus.gump?id=<bean:write name="depends" property="id"/>"><bean:write name="depends" property="projectName"/></a></li>
	 	</logic:iterate>
	 	</ul>
	 	</p>
	 	<p>
	 	Package directly depending on this package:
	 	<ul>
	 	<logic:iterate id="dependees" name="project" property="dependeesList">
	 		<li><a href="ProjectStatus.gump?id=<bean:write name="dependees" property="id"/>"><bean:write name="dependees" property="projectName"/></a></li>
	 	</logic:iterate>
	 	</ul>
	 	</p>
	 </p>

 	<h3>History</h3>
 	<p><bean:define id="history" name="project" property="history" /></p>

 	<table>
	 	<tr><td>Current State:</td><td><bean:write name="history" property="currentStateString"/></td></tr>
	 	<tr><td>Duration of State:</td><td><bean:write name="history" property="durationInState"/></td></tr>
	 	<tr><td>Start of State:</td><td><bean:write name="history" property="startOfState"/></td></tr>
		<tr><td>Previus State:</td><td><bean:write name="history" property="previusStateString"/></td></tr>
		<tr><td>Number of Success:</td><td><bean:write name="history" property="numberOfSuccess"/></td></tr>
		<tr><td>Number of Failures:</td><td><bean:write name="history" property="numberOfFailures"/></td></tr>
		<tr><td>Number of Stalled:</td><td><bean:write name="history" property="numberOfStalled"/></td></tr>
		<tr><td>Last Success:</td><td><bean:write name="history" property="lastSuccess"/></td></tr>
		<tr><td>First Success:</td><td><bean:write name="history" property="firsSuccess"/></td></tr>
	</table>
</div>

</div>

<%@ include file="/bottom.inc" %>







