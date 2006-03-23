<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>

<div id="top">
 <ul class="path">
  <li><a href="../index.jsp" title="Home">Home</a></li>
  <li><a href="./" title="Results">Results</a></li>
  <li><a href="Builds.gump" title="By Builds">By Builds</a></li>
  <logic:present name="currentWorkspace"><li><a href="ShowRuns.gump?workspace=<bean:write name="currentWorkspace"/>" title="Select Run">Select Run</a></li></logic:present>
  <li class="current">Build Results</li>
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>

<div id="body">

    <h1>Build Results</h1>

      	<h3>Over all Statistic</h3>
      	
      	<p>A short presentation of how many package succeded. faild and stalled for this build.</p>
      	
		<table class="data">
		  <tr>
			<logic:iterate id="overAll" name="runsStatus" property="overAll">
			  <td class="<bean:write name="overAll" property="name"/>-left">
			    <bean:write name="overAll" property="name"/>
			  </td>
			  <td id="overall" class="<bean:write name="overAll" property="name"/>">
			  	<bean:write name="overAll" property="value"/> ( <bean:write name="overAll" property="percentage"/>% )
			  </td>
			</logic:iterate>   
		  </tr>
		</table>

		<h3>Project status</h3>

	    <table class="data">
	      <thead>
  		  <tr><th>Project Name</th><th>dependees</th><th>direct dependees</th><th>start</th><th>end</th><th>result</th></tr>
  		  </thead>
  		  <tbody>
		  <logic:iterate id="build" indexId="index2" name="runsStatus" property="builds">    
		  <bean:define id="cssClass" name="build" property="resultString"/>
		    <tr>
 			  <td class="<bean:write name="cssClass" />-left"><a href="ProjectStatus.gump?id=<bean:write name="build" property="id"/>"><bean:write name="build" property="projectName"/></a></td>
 			  <td class="<bean:write name="cssClass" />"><bean:write name="build" property="dependees"/></td>
 			  <td class="<bean:write name="cssClass" />"><bean:write name="build" property="directDependees"/></td>
 			  <td class="<bean:write name="cssClass" />"><bean:write name="build" property="startTime"/></td>
 			  <td class="<bean:write name="cssClass" />"><bean:write name="build" property="endTime"/></td> 
 			  <td class="<bean:write name="cssClass" />"><bean:write name="build" property="resultString"/></td>  
		    </tr>
		  </logic:iterate>
		  </tbody>
       	</table>
</div>

</div>

<%@ include file="/bottom.inc" %>
