import Foundation

let src = CGEventSource(stateID: CGEventSourceStateID.hidSystemState)
    
let k1 = CGEvent(keyboardEventSource: src, virtualKey: 0x03, keyDown: true)   // space-down
let k2 = CGEvent(keyboardEventSource: src, virtualKey: 0x37, keyDown: true)   // space-down
let k3 = CGEvent(keyboardEventSource: src, virtualKey: 0x37, keyDown: false)  // space-up
let k4 = CGEvent(keyboardEventSource: src, virtualKey: 0x03, keyDown: false)  // space-up

let pids = [ 549 ]; // real PID-s from command 'ps -ax' - e.g. for example 3 different processes
    
for i in 0 ..< pids.count {
    print("sending to pid: ", pids[i]);
    k1?.postToPid( pid_t(pids[i]) ); // convert int to pid_t
    k2?.postToPid( pid_t(pids[i]) );
    k3?.postToPid( pid_t(pids[i]) );
    k4?.postToPid( pid_t(pids[i]) );
}
