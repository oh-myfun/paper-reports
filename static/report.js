(function(){
  var pi=document.getElementById('progressIndicator');
  var fill=document.getElementById('progressFill');
  var text=document.getElementById('progressText');
  var C=2*Math.PI*22;
  fill.style.strokeDasharray=C;
  fill.style.strokeDashoffset=C;
  function update(){
    var st=window.pageYOffset||document.documentElement.scrollTop;
    var sh=document.documentElement.scrollHeight-window.innerHeight;
    var p=sh>0?st/sh:0;
    p=Math.min(p,1);
    fill.style.strokeDashoffset=C*(1-p);
    text.textContent=Math.round(p*100)+'%';
    pi.classList.toggle('visible',st>200);
  }
  pi.onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
  window.addEventListener('scroll',update,{passive:true});
  update();

  var lb=document.getElementById('lightbox');
  var lbImg=document.getElementById('lightboxImg');
  var scale=1,tx=0,ty=0,dragging=false,lastX=0,lastY=0;

  document.querySelectorAll('.figure img').forEach(function(img){
    img.style.cursor='zoom-in';
    img.onclick=function(e){
      e.stopPropagation();
      lbImg.src=img.src;
      lb.classList.add('active');
      scale=1;tx=0;ty=0;
      lbImg.style.transform='scale(1) translate(0,0)';
    };
  });
  lb.onclick=function(e){
    if(e.target===lbImg)return;
    lb.classList.remove('active');
  };
  document.addEventListener('keydown',function(e){if(e.key==='Escape')lb.classList.remove('active')});

  lbImg.addEventListener('wheel',function(e){
    e.preventDefault();
    var d=e.deltaY>0?-0.08:0.08;
    scale=Math.max(0.5,Math.min(scale+d,5));
    lbImg.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
  },{passive:false});

  lbImg.addEventListener('mousedown',function(e){
    e.preventDefault();
    dragging=true;lastX=e.clientX;lastY=e.clientY;
    lbImg.style.cursor='grab';
  });
  window.addEventListener('mousemove',function(e){
    if(!dragging)return;
    tx+=e.clientX-lastX;ty+=e.clientY-lastY;
    lastX=e.clientX;lastY=e.clientY;
    lbImg.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
  });
  window.addEventListener('mouseup',function(){
    dragging=false;
    lbImg.style.cursor='zoom-out';
  });
  lbImg.style.cursor='zoom-out';
})();
