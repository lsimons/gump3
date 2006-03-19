<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>




<%@ include file="/results/top.inc" %>


<div id="top">
 <ul class="path">
	Error Page
 </ul>
</div>

<div id="center">

<%@ include file="/results/topMenu.inc" %>




<div id="body">

    <h1>Error!!</h1><br />
    <p>
    <ul>
    An Error has occured!<br />
    <p>
<!--     <logic:present name="errorMsg">
	    <bean:write name="errorMsg"/>
    </logic:present>
    <logic:notPresent>  -->
    	An error has accured one reason might be that the session has expired.<br /> Please try again!
<!--     </logic:notPresent> -->
    </p>
    </ul>
    </p>
</div>

</div>

<%@ include file="/results/bottom.inc" %>







