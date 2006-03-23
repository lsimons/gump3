package org.apache.gump.dynagump.actions;

import java.sql.SQLException;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.database.CouldNotFindDBException;
import org.apache.gump.dynagump.database.DBHandler;
import org.apache.gump.dynagump.database.controller.DBController;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

public class ListProjectBuilds extends Action {
    private static Log log = LogFactory.getLog(ProjectStatusAction.class);

    public ActionForward execute(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) {

        boolean forward = true;
        String errorMsg = null;

        try {
            String id = request.getParameter("id");
            if (id == null || id.equals("")) {
                id = (String) request.getSession().getAttribute("projectId");
            }
            if (id == null) {
                throw new RuntimeException("No Run project slected!\n You have to select a project in order to see all its builds");
            }
            DBController db = DBHandler.getController();
            List builds = db.getProjectBuildsList(id);
            request.getSession().setAttribute("projects", builds);
        } catch (SQLException sqle) {
            log.error(sqle.getMessage());
            sqle.getStackTrace();
            errorMsg = sqle.getMessage();
            forward = false;
        } catch (CouldNotFindDBException cnfdbe) {
            log.error(cnfdbe.getMessage());
            cnfdbe.getStackTrace();
            errorMsg = cnfdbe.getMessage();
            forward = false;
        } catch (RuntimeException e) {
            log.error(e.getMessage());
            e.getStackTrace();
            errorMsg = e.getMessage();
            forward = false;
        }

        if (forward == true) {
            return mapping.findForward("success");
        } else {
            request.getSession().setAttribute("errorMsg", errorMsg);
            return mapping.findForward("error");
        }
    }
}
