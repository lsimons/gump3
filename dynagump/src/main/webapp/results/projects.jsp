<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>

<div id="top">
 <ul class="path">
  <li><a href="../index.jsp" title="Home">Home</a></li>
  <li><a href="./" title="Results">Results</a></li>
  <li class="current">Project List</li>
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>

<div id="body">

    <h1>Projects</h1>
    
    <table class="data">
    <thead>
    <tr><th>Project name</th><th>Description</th><th>module</th></tr>
    </thead>
    <tbody>
    <logic:iterate id="project" name="projects">
    	 <tr>
    	  <td>
    		<a href="ListProjectBuild.gump?id=<bean:write name="project" property="projectId"/>"><bean:write name="project" property="name"/></a>
    	  </td>
    	  <td>
    		<bean:write name="project" property="description"/>
    	  </td>
    	  <td>
    		<bean:write name="project" property="moduleName"/>
    	  </td>
    	 </tr>
    </logic:iterate>
    </tbody>
    </table>

</div>

</div>

<%@ include file="/bottom.inc" %>







