package org.apache.gump.dynagump.presentation.actions;

import java.sql.SQLException;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.gump.dynagump.presentation.database.CouldNotFindDBException;
import org.apache.gump.dynagump.presentation.database.DBHandler;
import org.apache.gump.dynagump.presentation.database.controller.DBController;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

public class ProjectListAction extends Action {

    private static Log log = LogFactory.getLog(ProjectStatusAction.class);

    public ActionForward execute(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) {

        boolean forward = true;
        String errorMsg = null;

        try {
            DBController db = DBHandler.getController();
            List projects = db.getProjects();
            request.getSession().setAttribute("projects", projects);
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
            return mapping.findForward("errorPriv");
        }
    }
}
