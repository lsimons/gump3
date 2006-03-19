package org.apache.gump.dynagump.presentation.valueObjects;

import java.io.Serializable;
/**
 * This object is an object to contain the over all status of a run or module.
 * @author hodden
 *
 */
public class StatusVO implements Serializable {

	private String name;
	private int value;
	private float percentage;
	
	public StatusVO(){}
	public StatusVO(String name, int value){
		this.name = name;
		this.value = value;
	
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public int getValue() {
		return value;
	}
	public void setValue(int value) {
		this.value = value;
	}
	public float getPercentage() {
		return percentage;
	}
	public void setPercentage(float percentage) {
		this.percentage = percentage;
	}
	public void calcPercent(int total){		
		this.percentage = Math.round(((float)value / total)*100);		
	}
	
}
