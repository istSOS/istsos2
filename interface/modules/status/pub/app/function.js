function getColor(d){      
    
    if(!d.name) 
        return 'rgba(200,200,200,1)';
    if (d.parent.name === verified)
        return ( 'rgba(255,255,0,1)');
    if(d.parent.name === ok )
        return 'rgba('+ ( getColorOk(d))+',230,0,1)';
    if (d.parent.name === notok)
        return ( 'rgba(255,' + getColorNot(d) + ',0,1)');
    if((d.name === ok ) || (d.name === notok) || d.name === verified)
        return 'rgba(150,150,150,1)';
    return 'rgba(200,200,200,1)';   
}

function getColorNot(d){
    return type==="cycle"? (200 - parseInt(((d.cycle - minCycle) / stepCycle),0)):(200- parseInt(((d.delay - minNot) / stepNot),0));
}

function getColorOk(d){return type ==="cycle" ? parseInt(230 * d.cycle,0) : (parseInt(((d.delay - minOk) / stepOk),0));}

function zoom(d) {

    tmpName = d.name;
    var kx = w / d.dx; 
    var ky = h  / d.dy;
    
    x.domain([d.x, d.x + d.dx]);
    y.domain([d.y,d.y + d.dy]); 
    
    
    var t = svg.selectAll("g.cell").transition().duration(1000)
        .attr("transform", function(d) {return "translate(" + x(d.x) + "," + y(d.y) + ")"; });
    
    t.select("rect")
        .attr("width",  function(d) {return kx * d.dx - 1; })
        .attr("height", function(d) {return ky * d.dy - 1; });  
    
    t.select("text")
        .attr("x", function(d) { return d.children ? 10 : kx * getX(d); })
        .attr("y", function(d) { return ky * getY(d); })
        .text(getText);
    
    d3.event.stopPropagation();   
}

function updateColor(){ svg.selectAll("g.cell").select("rect").style("fill", getColor);}

function getX(d){ return !d.children ? (d.dx/2) : 10;}

function getY(d){ return !d.children ? (d.dy/2) : 10;}

function getStroke(d){ return d.parent == root ? 3 : 0;}

function updateResult(d){
    if(!d.children && d.name){
        var popupText = 'name    : ' + d.name + '<br/>';
        popupText += 'delay : ' + d.delay + '<br/>';
        popupText += 'cycle : ' + d.cycle + '<br/>';
        
        if(d.code) popupText += 'code : ' + d.code + '<br/>';
        
        if(d.exceptions) popupText += 'details : ' + d.exceptions[0].details + '<br/>';
        d3.select('#popup').style('visibility','visible').html(popupText);
    }
}

function clearResult(){ d3.select('#popup').style('visibility','hidden');}

function movePopup(d){
    if(!d.children && d.name){
        d3.select('#popup').style("top", (d3.event.pageY - 150)+"px").style("left",(d3.event.pageX + 10)+"px");
    }
}

function getText(d){ 
    if(d.children){
        return d.name;
    }else{
        if(tmpName === verified || tmpName === notok){   
            return d.code ? (d.name +" " + ((d.code.length > 1) ? d.code[0] + " *": d.code[0])) : d.name;
        } else{
            return d.code ? ((d.code.length > 1) ? d.code[0] + " *": d.code[0]) : (d.parent.name == tmpName ? d.name :"");
        }
    }
}

function getDelay(d){return d.delay;}
function getCycle(d){return d.cycle;}

function exceptionPage(d){
        
    var myForm = Ext.create('istsosStatus.view.ProcView');

    
    myForm.extraParams = {d: d};
    
    myForm.show();
}