<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>


<div id="top">
 <ul class="path">
  <li><a href="/index.jsp" title="Home">Home</a></li>
  <li><a href="./index.jsp" title="Results">Results</a></li>
  <li><a href="Workspaces.gump" title="By Builds">By Builds</a></li>
  <li class="current">Runs</li>
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>

<%@ include file="/leftBar.inc" %>

<div id="body" class="withside">

    <h1>Select Run</h1>

    <table class="data">
    <thead>
    <tr><th>Name</th><th>start</th><th>end</th></tr>
    </thead>
    <tbody>
    <logic:iterate id="run" indexId="index" name="runs">
		<tr>
			<td><a href="StatusRun.gump?id=<bean:write name="run" property="id"/>"><bean:write name="run" property="name"/></a></td>
			<td><bean:write name="run" property="start"/></td>
			<td><bean:write name="run" property="end"/></td>
		</tr>
    </logic:iterate>
    </tbody>
    </table>
</div>

</div>

<%@ include file="/bottom.inc" %>







