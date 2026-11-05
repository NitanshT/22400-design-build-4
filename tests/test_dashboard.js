const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const src = fs.readFileSync("adafruit_io_frontend/app.js", "utf8");
function between(a, b) { const i=src.indexOf(a), j=src.indexOf(b,i); assert(i>=0 && j>i); return src.slice(i,j); }
const data = new Map();
const storage = {getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)};
const elements={rememberAioKey:{checked:false},aioKey:{value:""}};
const ctx={localStorage:storage,STORAGE_KEY:"settings",elements, setStatus:()=>{}, getSettingsFromForm:()=>({username:"user",aioKey:"secret"}),setFormFromSettings:s=>{ctx.form=s}, console};
vm.createContext(ctx);
vm.runInContext(between("function saveSettings()", "function clearSettings()") + between("function csvCell(", "function exportLatestCsv()"),ctx);
ctx.saveSettings(); assert(!JSON.parse(data.get("settings")).aioKey);
elements.rememberAioKey.checked=true; ctx.saveSettings(); assert.equal(JSON.parse(data.get("settings")).aioKey,"secret");
data.set("settings",JSON.stringify({username:"user",aioKey:"old"})); ctx.loadSettings();
assert(!JSON.parse(data.get("settings")).aioKey); assert(!ctx.form.aioKey);
assert.equal(ctx.csvCell("=1+1"), "\"'=1+1\"");
assert.equal(ctx.csvCell(" -1+2"), "\"' -1+2\"");
assert.equal(ctx.csvCell(-2.5,true), "\"-2.5\"");
assert.equal(ctx.csvCell('a"b'), '"a""b"');
console.log("dashboard storage and CSV tests passed");

async function testPolling() {
  let rejectPoll, calls=0;
  const session={recordingGaps:[],stoppedAt:null};
  const settings={limit:2};
  const polling={latestSettings:settings,refreshInFlight:false,activeExperimentSession:session,latestResults:[],getActiveSensors:()=>[{feedKey:"light"}],setStatus:()=>{},fetchFeedData:()=>{calls++; return new Promise((resolve,reject)=>{rejectPoll=reject;});},addResultsToActiveExperimentSession:()=>{},renderSummary:()=>{},renderCharts:()=>{},renderSensorCards:()=>{},renderTable:()=>{},console};
  vm.createContext(polling);
  vm.runInContext(between("async function refreshData()", "function startAutoRefresh("),polling);
  const first=polling.refreshData();
  await polling.refreshData();
  assert.equal(calls,1, "polls must not overlap");
  rejectPoll(new Error("offline")); await first;
  assert.equal(session.recordingGaps.length,1);
  assert.deepEqual(Array.from(session.recordingGaps[0].feeds),["light"]);
  assert.equal(polling.refreshInFlight,false);
  polling.fetchFeedData=async()=>({sensor:{feedKey:"light"},points:[{},{}],error:null});
  await polling.refreshData();
  assert.match(session.recordingGaps[1].reason,/history limit/);
  console.log("dashboard serialized polling and gap tests passed");
}
testPolling().catch(error=>{console.error(error);process.exitCode=1});
