package org.apache.gump.dynagump.presentation.database.controller;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

import org.apache.gump.dynagump.presentation.database.hibernate.BuildHib;
import org.apache.gump.dynagump.presentation.database.hibernate.DependenciesHib;
import org.apache.gump.dynagump.presentation.database.hibernate.HibernateUtil;
import org.apache.gump.dynagump.presentation.database.hibernate.HostsHib;
import org.apache.gump.dynagump.presentation.database.hibernate.ProjectHib;
import org.apache.gump.dynagump.presentation.database.hibernate.ProjectVersionIdHib;
import org.apache.gump.dynagump.presentation.database.hibernate.RunsHib;
import org.apache.gump.dynagump.presentation.database.hibernate.WorkspaceHib;
import org.apache.gump.dynagump.presentation.valueObjects.Build;
import org.apache.gump.dynagump.presentation.valueObjects.HistoryVO;
import org.apache.gump.dynagump.presentation.valueObjects.Host;
import org.apache.gump.dynagump.presentation.valueObjects.ProjectBuildVO;
import org.apache.gump.dynagump.presentation.valueObjects.ProjectVO;
import org.apache.gump.dynagump.presentation.valueObjects.Run;
import org.apache.gump.dynagump.presentation.valueObjects.RunStatusVO;
import org.apache.gump.dynagump.presentation.valueObjects.WorkSpace;
import org.hibernate.Session;

public class HibernateController implements DBController {

    public HibernateController() {

    }

    public List<Host> getHosts() throws SQLException {
        List<Host> li = new LinkedList<Host>();
        Session session = HibernateUtil.currentSession();
        Iterator it = session.createQuery("from HostsHib").list().iterator();
        Host hostVO;
        while (it.hasNext()) {
            HostsHib host = (HostsHib) it.next();
            Iterator wit = host.getWorkspace().iterator();
            hostVO = new Host(host.getAddress(), host.getDescription(), host.getCpuArch(), host.getCpuNumber(), host.getCpuSpeed(), host.getMemoryMb(), host.getDiskGB(), host.getName());
            while (wit.hasNext()) {
                WorkspaceHib wh = (WorkspaceHib) wit.next();
                hostVO.addWorkspace(new WorkSpace(wh.getId(), wh.getName(), wh.getHost(), wh.getDescription()));
            }
            li.add(hostVO);
        }
        return li;
    }

    public void setWorkspace(List<Host> li) throws SQLException {
    }

    public List<Run> getRuns(String workspace) throws SQLException {
        List<Run> li = new LinkedList<Run>();
        Session session = HibernateUtil.currentSession();
        Iterator<RunsHib> it = session.createQuery("from RunsHib where workspaceId='" + workspace + "'").list().iterator();
        RunsHib tempRun;
        while (it.hasNext()) {
            tempRun = it.next();
            li.add(new Run(tempRun.getId(), tempRun.getStartTime(), tempRun.getEndTime(), tempRun.getWorkspaceId().getId(), tempRun.getName()));
        }
        return li;
    }

    public void getBuilds(RunStatusVO r, String id) throws SQLException {

        Session session = HibernateUtil.currentSession();
        Iterator<BuildHib> it = session.createQuery("from BuildHib where runId='" + id + "'").list().iterator();
        while (it.hasNext()) {
            BuildHib bh = it.next();
            ProjectHib ph = bh.getProjectId().getProject();
            r.addBuild(new Build(bh.getBuildId(), bh.getRunId().getId(), bh.getProjectId().getId(), bh.getStartTime(), bh.getEndTime(), bh
                    .getResult().getId(), bh.getLog(), bh.getResult().getName(), ph.getName(), ph.getId(), ph.getDescription(), ph.getModule()
                    .getName()));
        }
    }

    public void setDependencies(RunStatusVO r) throws SQLException {
        HashMap<String, Build> builds = r.getBuildsMap();

        Set<String> keys = builds.keySet();
        Iterator<String> it = keys.iterator();
        String key = null;
        while (it.hasNext()) {

            key = it.next();

            Session session = HibernateUtil.currentSession();
            Iterator<DependenciesHib> depIt = session.createQuery("from DependenciesHib where dependant='" + builds.get(key).getProjectVersionId() + "'").list().iterator();

            /*
             * while(depIt.hasNext()){ System.out.println(i++); String Bid =
             * depIt.next().getBuild().getRunId(); System.out.println("id:
             * "+Bid+" key: "+key+" build:"+ builds.get(Bid));
             * 
             * builds.get(key).addDependees(builds.get(Bid)); }
             */

        }

    }

    public void addHistory(Build b) throws SQLException {
        Session session = HibernateUtil.currentSession();
        ProjectHib ph = (ProjectHib) session.load(org.apache.gump.dynagump.presentation.database.hibernate.ProjectHib.class, b.getProjectId());
        HistoryVO history = new HistoryVO();
        Iterator<ProjectVersionIdHib> it = ph.getProjectVersion().iterator();

        while (it.hasNext()) {

            BuildHib bh = it.next().getBuild();
            history.addValues(bh.getResult().getId(), bh.getStartTime());
            history.setValues();
        }
        b.addHistory(history);
    }

    public List<ProjectVO> getProjects() throws SQLException {
        List<ProjectVO> li = new LinkedList<ProjectVO>();
        Session session = HibernateUtil.currentSession();
        Iterator<ProjectHib> phIt = session.createQuery("from ProjectHib").list().iterator();
        while (phIt.hasNext()) {
            ProjectHib ph = phIt.next();
            li.add(new ProjectVO(ph.getId(), ph.getName(), ph.getDescription(), ph.getModule().getId(), ph.getModule().getName()));
        }

        return li;
    }

    public List<ProjectBuildVO> getProjectBuildsList(String projectID) throws SQLException {
        List<ProjectBuildVO> li = new LinkedList<ProjectBuildVO>();
        Session session = HibernateUtil.currentSession();
        ProjectHib ph = (ProjectHib) session.load(org.apache.gump.dynagump.presentation.database.hibernate.ProjectHib.class, projectID);
        Iterator<ProjectVersionIdHib> it = ph.getProjectVersion().iterator();
        while (it.hasNext()) {
            ProjectBuildVO tempVO = null;
            ProjectVersionIdHib pvih = it.next();
            BuildHib buildhib = pvih.getBuild();

            tempVO = new ProjectBuildVO();
            tempVO.setId(buildhib.getBuildId());
            tempVO.setName(ph.getName());
            tempVO.setDescription(ph.getDescription());
            tempVO.setModule_id(ph.getModule().getId());
            tempVO.setModule_name(ph.getModule().getName());
            tempVO.setBuild_id(buildhib.getBuildId());
            tempVO.setRun_id(buildhib.getRunId().getId());
            tempVO.setRun_name(buildhib.getRunId().getName());
            tempVO.setResult(buildhib.getResult().getId());

            tempVO.setResultString(buildhib.getResult().getName());
            tempVO.setEnd_time(buildhib.getEndTime());
            tempVO.setStart_time(buildhib.getStartTime());
            tempVO.setWorkspace_id(buildhib.getRunId().getWorkspaceId().getId());
            tempVO.setWorkspace_name(buildhib.getRunId().getWorkspaceId().getName());
            tempVO.setProjectVersionID(pvih.getId());
            li.add(tempVO);
        }

        return li;
    }
}
