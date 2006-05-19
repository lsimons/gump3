<%@ taglib uri="/WEB-INF/struts-bean.tld" prefix="bean" %>
<%@ taglib uri="/WEB-INF/struts-logic.tld" prefix="logic" %>

<%@ include file="/top.inc" %>

<div id="center">

<div id="body">

    <h1>Error!!</h1>
    
    <p>An Error has occured!</p>
    
    <p>
      <logic:present name="errorMsg">
	    <bean:write name="errorMsg"/>
      </logic:present>
     <logic:notPresent>
    	    An error has accured one reason might be that the session has expired.<br /> Please try again!
     </logic:notPresent>
    </p>
</div>

</div>

<%@ include file="/bottom.inc" %>







