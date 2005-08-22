<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>




<%@ include file="/results/top.inc" %>


<div id="top">
 <ul class="path">
  <li><a href="../index.jsp" title="Home">Home</a></li>
  <li><a href="./" title="Results">Results</a></li>
  By Builds
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>


<%@ include file="/leftBar.inc" %>

<div id="body" class="withside">

    <h1>Select Workspace</h1><br />
    <p>
    <ul>
    <logic:iterate id="host" indexId="index" name="workspaces">

      <b><bean:write name="host" property="name"/> - <bean:write name="host" property="description"/></b><br />
    	<p>
    	<logic:iterate id="workspace" indexId="index2" name="host" property="workspaces">
		
		 <ul>
    		<li>
    			<a href="ShowRuns.gump?workspace=<bean:write name="workspace" property="id"/>"><bean:write name="workspace" property="name"/></a> - <bean:write name="workspace" property="description"/>
		    </li>
    	 </ul>
	    </logic:iterate>
		</p>
    </logic:iterate>
    </ul>
    </p>
</div>

</div>

<%@ include file="/results/bottom.inc" %>







