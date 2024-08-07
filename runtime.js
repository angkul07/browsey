console = { log: function(x) {call_python("log", x);}}

document = {querySelectorAll: function(s){
    var handles = call_python("querySelectorAll", s);
    return handles.map(function(h) {return new Node(h)});
}}

function Node(handle) {this.handle = handle;}

Node.prototype.getAttribute = function(attr){
    return call_python("getAttribute", this.handle, attr);
}

inputs = document.querySelectorAll('input')
for (var i = 0; i < inputs.length; i++) {
    var name = inputs[i].getAttribute("name");
    var value = inputs[i].getAttribute("value");
    if (value.length > 100) {
        console.log("Input " + name + " has too much text.")
    }
}