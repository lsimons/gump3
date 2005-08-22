package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
/**
 * Value object to collect all the information from one Run. 
 * Contains a list of builds for this run. 
 * And the over all status for this run.
 * @author hodden
 *
 */
public class RunStatusVO implements Serializable{
	
	private HashMap overAllStatus;
	private HashMap<String, Build> builds = new HashMap<String, Build>();
	
	public RunStatusVO(){
		
	}
	public void addBuild(Build b){
		builds.put(b.getId(), b);
	}
	public Collection<Build> getBuilds() {		
		Collection<Build> c = builds.values();
		return c;
	}
	public HashMap<String, Build> getBuildsMap() {		
		return builds;
	}

	public void setBuilds(HashMap<String, Build> builds) {
		this.builds = builds;
	}
	public List<StatusVO> getOverAll(){
		List<StatusVO> li = new LinkedList<StatusVO>();
		li.add(new StatusVO("success", 0));
		li.add(new StatusVO("failure", 0));
		li.add(new StatusVO("stalled", 0));
		this.updateOverAllStats(li);
		this.setPercentage(li);
		return li;
	}
	public Build getBuild(String id){
		return builds.get(id);	
	}
	private void setPercentage(List<StatusVO> li){
		for(int i=0; i<li.size(); i++){
			li.get(i).calcPercent(builds.size());
		}
	}
	private void updateOverAllStats(List<StatusVO> li){
		HashMap<String, StatusVO> status = new HashMap<String, StatusVO>();
		//TODO Initiate the list from the result table
		for(int i=0; i < li.size(); i++){
			status.put(li.get(i).getName(), li.get(i));
		}
		StatusVO temp;
		Set<String> s = builds.keySet();
		Iterator<String> it = s.iterator();
		while(it.hasNext()){
			temp = status.get(builds.get(it.next()).getResultString());
			temp.setValue(temp.getValue()+1); 
		}
	}
}
