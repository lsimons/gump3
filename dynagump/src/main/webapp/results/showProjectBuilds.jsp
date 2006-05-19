<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>

<div id="top">
 <ul class="path">
  <li><a href="/index.jsp" title="Home">Home</a></li>
  <li><a href="./index.jsp" title="Results">Results</a></li>
  <li><a href="">Project List</a></li>
  <li class="current">Project Builds</li>
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>

<div id="body">

    <h1>Project Builds</h1>

    <table class="data">
    <thead>
    <tr><th>Project name</th><th>depends on</th><th>dependees</th><th>Start time</th><th>Workspace</th><th>Run</th><th>Result</th><th>module</th></tr>
    </thead>
    <tbody>
    <logic:iterate id="project" name="projects">
    	 <tr>
    	  <td>
    		<bean:write name="project" property="name" />
    	  </td>
    	  <td>
    		<bean:write name="project" property="numbersOfDependant" />
    	  </td>
    	  <td>
    		<bean:write name="project" property="numbersOfDependees" />
    	  </td>
    	  <td>
    		<bean:write name="project" property="start_time" />
    	  </td>
    	  <td>
    		<a href="ShowRuns.gump?workspace=<bean:write name="project" property="workspace_id"/>">
    		  <bean:write name="project" property="workspace_name" />
    		</a>
    	  </td>
    	  <td>
    		<a href="StatusRun.gump?id=<bean:write name="project" property="run_id"/>">
	    		<bean:write name="project" property="run_name" />
	    	</a>
       </td>
       <td>
    		<bean:write name="project" property="resultString" />
    	   </td>
    	   <td>
    		<bean:write name="project" property="module_name" />
       </td>
      </tr>
    </logic:iterate>
    </tbody>
    </table>

</div>

</div>

<%@ include file="/bottom.inc" %>







