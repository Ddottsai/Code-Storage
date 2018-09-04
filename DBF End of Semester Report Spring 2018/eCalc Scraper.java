import org.jsoup.Jsoup;
import org.jsoup.nodes.Element;
import java.io.*;
import java.net.MalformedURLException;
import java.util.*;

import com.gargoylesoftware.htmlunit.html.*;

import com.gargoylesoftware.htmlunit.WebClient;
import com.gargoylesoftware.htmlunit.BrowserVersion;
import com.gargoylesoftware.htmlunit.FailingHttpStatusCodeException;

public class Parser3 {
	
	
	static final Random r = new Random();
	static  String Ptwist; // -5,-2.5,0,2,2.5,3.5,4,4.5
	static  String inGWeight = String.valueOf(r.nextGaussian() * 1500 + 5000);
	static  String inMPoles = rands(8,14,1).get(0);
	static  String inGWingArea = rands(30,100,1).get(0);
	static  String inGDragCd = String.valueOf(r.nextGaussian()*0.015+0.06);
	static  String inPConst = rands(1.2,1.7,1).get(0);
	static  String inTConst = rands(0.85,1.0,1).get(0);
	static  String inBVcell = rands(6,18,1).get(0);
	static String inBP =String.valueOf((new int[]{1,1,1,1,2,2,2,3,3})[r.nextInt(9)]);
	static String inBCcont = String.valueOf((new int[]{6,8,10,12,14,18,20,22})[r.nextInt(8)]);
	
	public static void main(String[] args) throws FileNotFoundException, IOException, InterruptedException{
    	final WebClient WEB_CLIENT = new WebClient(BrowserVersion.CHROME);
    	PrintWriter pw;
    	boolean notDone = false;
		final StringBuilder text = new StringBuilder(1300);
    	final int inputIndices[];
    	final DomElement inputFields[];
    	String inputVals[][];
    	HashMap<String, ArrayList<String>> inputMap = new HashMap<String, ArrayList<String>>();
    	final DomElement[] dynamicOutputElems;
    	final Tuple [] dependentInputs;
 //   	String strForSpeed = null;
 //   	Elements elemsForSpeed = null;
    	
//    	final HashMap<String,Integer> tempInputMapIndices = new HashMap<String,Integer>();
//    	String[] tempinputMapKeys;
		WEB_CLIENT.getOptions().setJavaScriptEnabled(true);
		java.util.logging.Logger.getLogger("com.gargoylesoftware").setLevel(java.util.logging.Level.OFF);
		WEB_CLIENT.getOptions().setThrowExceptionOnFailingStatusCode(false);
		WEB_CLIENT.getOptions().setThrowExceptionOnScriptError(false);
		WEB_CLIENT.getOptions().setPrintContentOnFailingStatusCode(false);
		
        try {
            HtmlPage loginPage = WEB_CLIENT.getPage("https://www.ecalc.ch/calcmember/login.php?https://www.ecalc.ch/motorcalc.php");
            HtmlForm loginForm = loginPage.getFormByName("siteloklogin");
            loginForm.getInputByName("username").setValueAttribute("designbuildfly@cornell.edu");
            loginForm.getInputByName("password").setValueAttribute("TakeFlight");
            loginForm.getElementsByTagName("button").get(0).click();
        } catch (FailingHttpStatusCodeException e) {
            e.printStackTrace();
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        WEB_CLIENT.waitForBackgroundJavaScriptStartingBefore(500);
        
    	HtmlPage page = (HtmlPage)WEB_CLIENT.getPage("https://www.ecalc.ch/motorcalc.php");
    	
    	WEB_CLIENT.waitForBackgroundJavaScriptStartingBefore(100);
    	
    	DomNodeList<DomElement> allInputFields = page.getElementsByTagName("INPUT");
    	DomNodeList<DomElement> allSelectFields = page.getElementsByTagName("SELECT");
    	
    	HtmlElement button = ((HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage() )
    			.getElementByName("btnCalculate");
    	
    	HtmlTable rpmTable = (HtmlTable) ((HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage() )
    			.getElementById("rpmTable");
			
   		ArrayList<DomNode> tempDynamicOuts = getDynamicOutputElems(WEB_CLIENT);
   		ArrayList<DomNode> toRemove = new ArrayList<DomNode>();
   		for (DomNode dynamicOut : tempDynamicOuts) {
   			String id = ((HtmlElement)dynamicOut).getId();
   			if (id.equals("outBCapacity") || id.equals("outBCapacity")
   					|| id.equals("outBWeight") || id.equals("outMVclimbSpeed")
   					|| id.equals("outTotAUW"))
   				toRemove.add(dynamicOut);
   		}
   		dynamicOutputElems = tempDynamicOuts.toArray(new DomElement[1]);
   		
    	WEB_CLIENT.waitForBackgroundJavaScriptStartingBefore(1000);
    	
   		page = ((HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage() );
		page.getElementById("inBWeight").setAttribute("value","50");
		page.getElementById("inBWeightOz").setAttribute("value","1.7637");
		page.getElementById("inEWeight").setAttribute("value","20");
		page.getElementById("inEWeightOz").setAttribute("value","0.705479");
		page.getElementById("inMLength").setAttribute("value","20");
		page.getElementById("inMLengthInch").setAttribute("value","0.79");
		page.getElementById("inMWeight").setAttribute("value","75");
		page.getElementById("inMWeightOz").setAttribute("value","2.6");
		
		

		DomElement errorMsg = ((HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage())
				.getElementById("errorMsg");
		dependentInputs = getDependencies(WEB_CLIENT);
		
		String[] temp;
    	
    	getInputs(inputMap);
    	
    	List<DomElement> tempInputFields = new ArrayList<DomElement>();
    	for (DomElement field : allInputFields) {
			if (inputMap.containsKey(field.getAttribute("id")))
				tempInputFields.add(field);
    	}
    	for (DomElement field : allSelectFields) {
			if (inputMap.containsKey(field.getAttribute("id")))
				tempInputFields.add(field);
    	}
		
   		inputIndices = new int[tempInputFields.size()]; // initialized to 0
		inputFields = new DomElement[tempInputFields.size()];
		
		for (int a = 0; a < tempInputFields.size(); a++) {
			inputFields[a] = tempInputFields.get(a);
		}
   		final int numFields = inputFields.length;
   		for (int repeat = 0; repeat < 100; repeat++) {
	   		final String time = String.valueOf(System.currentTimeMillis());
	   		p("making new file, #" + repeat + "...");
			pw = new PrintWriter(new BufferedWriter(new FileWriter("Rands" + time + ".csv")));
			printInputOutputNamesToCSV(pw,inputFields, dynamicOutputElems,WEB_CLIENT);
	    	for (int overallOverallIter = 0; overallOverallIter < 5; overallOverallIter++) {
	    		Ptwist = String.valueOf((new double[] {-5,-2.5,-2.5,0,0,0,2,2,2.5,2.5,3,3.5,4,4.5})[r.nextInt(14)]);
				inGWeight = String.valueOf(r.nextGaussian() * 1750 + 4000).substring(0, 4);
				inMPoles = rands(8,14,1).get(0);
				inGWingArea = rands(30,100,1).get(0);
				inGDragCd = String.valueOf(r.nextGaussian()*0.015+0.06).substring(0,6);
				inPConst = rands(1.2,1.7,1).get(0);
				inTConst = rands(0.85,1.0,1).get(0);
				inBVcell = rands(6,18,1).get(0);
				inBP = String.valueOf((new int[]{1,1,1,1,2,2,2,3,3})[r.nextInt(9)]);
				inBCcont = String.valueOf((new double[]{6,8,10,12,14,18,20,22})[r.nextInt(8)]);
				
		    	page.getElementById("inPTwist").setAttribute("value",Ptwist);
				page.getElementById("inGWeight").setAttribute("value",inGWeight);
				page.getElementById("inMPoles").setAttribute("value", inMPoles);
				page.getElementById("inGWingArea").setAttribute("value", inGWingArea);
				page.getElementById("inGDragCd").setAttribute("value", inGDragCd);
				page.getElementById("inPConst").setAttribute("value", inPConst);
				page.getElementById("inTConst").setAttribute("value", inTConst);
				page.getElementById("inBVcell").setAttribute("value", inBVcell);
				page.getElementById("inBP").setAttribute("value",inBP);
				page.getElementById("inBCcont").setAttribute("value",inBCcont);
		    	p("  starting " + overallOverallIter + "...");
		    	
		   		for (int overallIter = 0; overallIter < 10; overallIter++) {
		
					int errorCount = 0;
					
					inputVals = getInputVals(inputFields);
					
			   		Arrays.fill(inputIndices,0);
			   		
			   		for (int a = 0; a < inputFields.length; a++)
			    		inputFields[a].setAttribute("value", inputVals[a][inputIndices[a]]);
			   		text.setLength(0);
			   		
				    do { // assume inputMap is not empty
				    	errorCount--;
				   		for (Tuple dependency : dependentInputs)
				   			dependency.fill();
				    	
				   		WEB_CLIENT.waitForBackgroundJavaScriptStartingBefore(0);
				        button.click();
						pw.print(text.toString());
						text.setLength(0);
				        WEB_CLIENT.waitForBackgroundJavaScriptStartingBefore(0);
				        
				       if (errorMsg.asText().contains("lead to a calculation error")) {
				    	   if (errorCount >= 12) {
					    	   notDone = false;
								for (int a = 0; a < numFields; a++) {
									temp = inputVals[a];
									if (inputIndices[a] != temp.length-1) {
										inputIndices[a]++;
										inputFields[a].setAttribute("value", temp[inputIndices[a]]);
									}
						         }
								errorCount=0;
					         }
				    	   else
				    	     errorCount+=4;
				       }
					   else {
							for (int a = 0; a < numFields; a++)
								text.append(inputFields[a].asText()).append(',');
							text.append(Ptwist).append(',')
								.append(inGWeight).append(',')
								.append(inMPoles).append(',')
								.append(inGWingArea).append(',')
								.append(inGDragCd).append(',')
								.append(inPConst).append(',')
								.append(inTConst).append(',')
								.append(inBVcell).append(',')
								.append(inBP).append(',')
								.append(inBCcont).append(',');
					   		
					   		for (DomNode elem : dynamicOutputElems)
					   			text.append(elem.asText()).append(',');
					   		
							for (Element elem : Jsoup.parse(rpmTable.asXml()).select("table > tbody > tr:gt(2) > td"))
								text.append(elem.text()).append(',');
							text.append('\n');
						}
				    	notDone = false;
						for (int a = 0; a < numFields; a++) {
							temp = inputVals[a];
							inputIndices[a]++;
							if (inputIndices[a] == temp.length) {
								inputIndices[a] = 0;
								inputFields[a].setAttribute("value", temp[inputIndices[a]]);
							}
							else {
								inputFields[a].setAttribute("value", temp[inputIndices[a]]);
								notDone = true;
								break;
							}
				         }
				    } while (notDone);
				    pw.flush();
				    p("          " + overallIter);
		    	}
	    	}
	    	pw.close();
   		}
   		WEB_CLIENT.close();
    	p("actually done");
	}
	
	public static Tuple[] getDependencies(WebClient WEB_CLIENT) {
		HtmlPage page = (HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage();
		ArrayList<Tuple> dependencies = new ArrayList<Tuple>();
		dependencies.add(new Tuple(page.getElementById("inBCellCap")
				,page.getElementById("inBCap"),1));
		dependencies.add(new Tuple(page.getElementById("inBCcont")
				,page.getElementById("inBCmax"),1));
		/*dependencies.add(new Tuple(page.getElementById("inBWeight")
				,page.getElementById("inBWeightOz"),0.035274));*/
		//inEWeightOz
		dependencies.add(new Tuple(page.getElementById("inEContCurrent")
				,page.getElementById("inEMaxCurrent"),1));
	
		return dependencies.toArray(new Tuple[1]);
	}
	
	public static void getInputs(HashMap<String, ArrayList<String>> inputMap) {
		inputMap.clear();
		//inputMap.put("inGWeight", rands(1500,6000,1));
		//C-rate
		/////////////////////inputMap.put("inEContCurrent", rands(50,300,2));
		inputMap.put("inEContCurrent", rands(30,200,1));
		inputMap.put("inERi", rands(0.01,0.05,1));
		inputMap.put("inMIo", rands(0.6,1.4,1));
		inputMap.put("inPDiameter", rands(5.0,14,3));
		//inPTwist
		inputMap.put("inPPitch", rands(1.0,8,3));
		inputMap.put("inMKv", rands(600,4000,3));
		inputMap.put("inMVIo", rands(6.0,14,1));
		inputMap.put("inMLimit", rands(50,300,1));
		//////////////////////inputMap.put("inMRi", rands(0.05,0.15,2));
		inputMap.put("inMRi", rands(0.05,0.25,1));
		//inputMap.put("inMPoles", rands(10,12,1));
		//////////inputMap.put("inBS", rands(4,16,2));
		inputMap.put("inBS", rands(2,16,2));
		inputMap.put("inBCellCap", rands(600,3000,2));
		inputMap.put("inBRi", rands(0.05,0.5,2));
		//inputMap.put("inGWingArea", rands(30,100,1));
		//inputMap.put("inGDragCd", rands(0.02,0.1,1));
	}
	
	public static String[][] getInputVals(DomElement[] inputFields) {
		HashMap<String, ArrayList<String>> inputMap = new HashMap<String, ArrayList<String>>();
		//inputMap.put("inGWeight", rands(1500,6000,1));
		//C-rate
		/////////////////////inputMap.put("inEContCurrent", rands(50,300,2));
		inputMap.put("inEContCurrent", rands(30,200,1));
		inputMap.put("inERi", rands(0.01,0.1,1));
		inputMap.put("inMIo", rands(0.6,1.4,1));
		inputMap.put("inPDiameter", rands(5.0,14,3));
		//inPTwist
		inputMap.put("inPPitch", rands(1.0,8,3));
		inputMap.put("inMKv", rands(600,4000,3));
		inputMap.put("inMVIo", rands(6.0,14,1));
		inputMap.put("inMLimit", rands(50,300,1));
		//////////////////////inputMap.put("inMRi", rands(0.05,0.15,2));
		inputMap.put("inMRi", rands(0.05,0.25,1));
		//inputMap.put("inMPoles", rands(10,12,1));
		inputMap.put("inBS", rands(2,16,2));
		inputMap.put("inBCellCap", rands(600,3000,2));
		inputMap.put("inBRi", rands(0.05,0.5,2));
		//inputMap.put("inGWingArea", rands(30,100,1));
		//inputMap.put("inGDragCd", rands(0.02,0.1,1));

		String[][] result = new String[inputFields.length][];
		for (int a = 0; a < inputFields.length; a++) {
			result[a] = inputMap.get(inputFields[a].getId()).toArray(new String[1]);
		}
		return result;
	}
	
	public static ArrayList<String> range(double start, double end, double interval){
		ArrayList<String> result = new ArrayList<String>();
		for (double i = start; i-0.0000000000000000000000001 <= end; i+=interval)
			result.add(String.valueOf(i));
		return result;
	}
	
	public static ArrayList<String> rands(double start, double end, int num) {
		ArrayList<String> result = new ArrayList<String>();
		for (int i = 0; i < num; i++)
			result.add(String.valueOf(Math.random()*(end-start) + start).substring(0,6));
		return result;
	}
	
	public static ArrayList<String> rands(int start, int end, int num) {
		ArrayList<String> result = new ArrayList<String>();
		for (int i = 0; i < num; i++)
			result.add(String.valueOf((int)(Math.random()*(end-start+1) + start)));
		return result;
	}
	
	
	public static void printInputOutputNamesToCSV(PrintWriter pw,DomElement[] inputFields,DomElement[] dynamicOuts, WebClient WEB_CLIENT) {
		StringBuilder sb = new StringBuilder();
		
		for (DomElement fieldName : inputFields)
			sb.append(fieldName.getId()).append(',');
		sb.append("Ptwist").append(',');
		sb.append("inGWeight").append(',');
		sb.append("inMPoles").append(',');
		sb.append("inGWingArea").append(',');
		sb.append("inGDragCd").append(',');
		sb.append("inPConst").append(',');
		sb.append("inTConst").append(',');
		sb.append("inBVcell").append(',');
		sb.append("inBP").append(',');
		sb.append("inBCcont").append(',');
		
		for (DomElement fieldName : dynamicOuts)
			sb.append(fieldName.getId()).append(',');
		
		Set<String> blacklist = new HashSet<String>();
		blacklist.add("outBWeightO");
		blacklist.add("outMaxTempF");
		blacklist.add("outPThrustOz");
		blacklist.add("outPStallThrustOz");
		blacklist.add("outPTipSpeedMph");
		blacklist.add("outPEfficiencyOzW");
		blacklist.add("outTotDriveWeightOz");
		blacklist.add("outTotAUWOz");
		blacklist.add("outMWLoadOz");
		blacklist.add("outMStallSpeedMph");
		blacklist.add("outMLevelSpeedMph");
		blacklist.add("outMVclimbSpeedMph");
		blacklist.add("outMRocFt");
		
		for (int i = 1; i<=15; i++) {
			sb.append("rpm " + i + ',');
			sb.append("Throttle(%) " + i + ',');
			sb.append("Current(DC) " + i + ',');
			sb.append("Voltage(DC) " + i + ',');
			sb.append("El. Power (W) " + i + ',');
			sb.append("Efficiency (%) " + i + ',');
			sb.append("Thrust (g) " + i + ',');
			sb.append("Thrust (oz) " + i + ',');
			sb.append("Spec. Thrust (g/W) " + i + ',');
			sb.append("Spec. Thrust (oz/W) " + i + ',');
			sb.append("Pitch Speed (km/h) " + i + ',');
			sb.append("Pitch Speed (mph) " + i + ',');
			sb.append("Speed (level) (km/h) " + i + ',');
			sb.append("Speed (level) (mph) " + i + ',');
			sb.append("Motor Run Time (s) " + i + ',');
		}
		
		pw.println(sb.toString());
	}
	
	public static ArrayList<DomNode> getDynamicOutputElems(WebClient WEB_CLIENT) {
		ArrayList<DomNode> out = new ArrayList<DomNode>();
		
		Set<String> blacklist = new HashSet<String>();
		blacklist.add("outBWeightO");
		blacklist.add("outMaxTempF");
		blacklist.add("outPThrustOz");
		blacklist.add("outPStallThrustOz");
		blacklist.add("outPTipSpeedMph");
		blacklist.add("outPEfficiencyOzW");
		blacklist.add("outTotDriveWeightOz");
		blacklist.add("outTotAUWOz");
		blacklist.add("outMWLoadOz");
		blacklist.add("outMStallSpeedMph");
		blacklist.add("outMLevelSpeedMph");
		blacklist.add("outMVclimbSpeedMph");
		blacklist.add("outMRocFt");
		
		HtmlPage page = (HtmlPage)WEB_CLIENT.getCurrentWindow().getEnclosedPage();
		
		DomNode table = page.getElementById("lblRemark")
				.getParentNode().getParentNode().getParentNode().getParentNode().getParentNode()
				.getNextElementSibling().getNextElementSibling();
			
		for (DomElement potentialParent : table.getHtmlElementDescendants()) {
			if (potentialParent.getAttribute("style").equals("text-align: right")) {
				HtmlElement textNode = (HtmlElement) potentialParent.getFirstElementChild();
				if (textNode != null && !blacklist.contains(((HtmlElement)textNode).getId())) {
					out.add(textNode);
				}
			}
		}
		return out;
	}
	
	public static boolean incrementInputs(DomElement[] inputFields, int[] inputIndices, String[][] inputVals, WebClient WEB_CLIENT) {
		String[] temp;
		for (int a = 0; a < inputIndices.length; a++) {
			temp = inputVals[a];
			inputIndices[a]++;
			if (inputIndices[a] == temp.length) {
				inputIndices[a] = 0;
				inputFields[a].setAttribute("value", inputVals[a][inputIndices[a]]);
			}
			else {
				inputFields[a].setAttribute("value", inputVals[a][inputIndices[a]]);
				return true;
			}
		}
		return false;
	}
	
	/*public static boolean incrementInputs(int i,HashMap<String, ArrayList<String>> inputMap, HashMap<String, Integer> inputMapIndices,String str) {
		for (DomElement field : inputFields) {
			strForSpeed = field.getAttribute("name");
			field.setAttribute("value",inputMap.get(strForSpeed).get(inputMapIndices.get(strForSpeed)));
		for (;--i>=0;) {
			str = inputMapKeys[i];
			if (inputMapIndices.get(str) == inputMap.get(str).size() - 1)
				inputMapIndices.put(str,0);
			else{
				inputMapIndices.put(str,inputMapIndices.get(str)+1);
				return true;
			}
		}
		return false;
		
	}*/
	
	public static void p(String string) {
		System.out.println(string);
	}
	
	public static void p(int i) {
		System.out.println(""+i);
	}
	
	public static void p(double i) {
		System.out.println(""+i);
	}
	
	public static class Tuple { 
		  public final DomElement x; 
		  public final DomElement y; 
		  public final double z; 
		  
		  public Tuple(DomElement x, DomElement y, double z) { 
		    this.x = x; 
		    this.y = y; 
		    this.z = z;
		  } 
		  
		  public void fill() {
			  y.setAttribute("value", String.valueOf(Double.valueOf(x.getAttribute("value"))*z));
		  }
	} 
	
}









