import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

bw_picker_new = """  function renderBwPicker(){
    if(!showBwPicker) return null;
    const grid = buildGrid(bwPickerYear, bwPickerMonth);
    
    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowBwPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
        React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
          React.createElement('div',{className:'cal-nav'},
            React.createElement('button',{className:'cal-arrow',onClick:()=>setBwPickerMonth(m=>{if(m===0){setBwPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('span',{className:'cal-month'},`${MONTHS[bwPickerMonth]} ${bwPickerYear}`),
            React.createElement('button',{className:'cal-arrow',onClick:()=>setBwPickerMonth(m=>{if(m===11){setBwPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          ),
          React.createElement('div',{className:'cal-weekdays'},
            WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
          ),
          React.createElement('div',{className:'cal-grid'},
            grid.map((d,i)=>{
              if(!d) return React.createElement('div',{key:i,className:'cal-day empty'});
              const k = toKey(new Date(bwPickerYear, bwPickerMonth, d));
              const isSel = k === bwDate;
              const cls = 'cal-day' + (isSel?' selected':'') + (k===todayKey()?' today':'');
              return React.createElement('div',{key:i,className:cls,onClick:()=>{
                setBwDate(k);
                setShowBwPicker(false);
              }},d);
            })
          )
        )
      )
    );
  }"""

custom_picker_new = """  function renderCustomPicker(){
    if(!showPicker) return null;
    const grid = buildGrid(pickerYear, pickerMonth);
    
    function handleDayClick(d) {
      const k = toKey(new Date(pickerYear, pickerMonth, d));
      if (!pickerStart) {
        setPickerStart(k); setPickerEnd(k);
      } else if (pickerStart && pickerEnd === pickerStart) {
        if (k < pickerStart) { setPickerStart(k); setPickerEnd(pickerStart); }
        else { setPickerEnd(k); }
      } else {
        setPickerStart(k); setPickerEnd(k);
      }
    }

    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
        React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
          React.createElement('div',{className:'cal-nav'},
            React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===0){setPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('span',{className:'cal-month'},`${MONTHS[pickerMonth]} ${pickerYear}`),
            React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===11){setPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          ),
          React.createElement('div',{className:'cal-weekdays'},
            WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
          ),
          React.createElement('div',{className:'cal-grid'},
            grid.map((d,i)=>{
              if(!d) return React.createElement('div',{key:i,className:'cal-day empty'});
              const k = toKey(new Date(pickerYear, pickerMonth, d));
              let cls = 'cal-day';
              if(data[k]) cls += ' has-workout';
              if(k === pickerStart || k === pickerEnd) cls += ' selected';
              if(k === pickerStart) cls += ' range-start';
              if(k === pickerEnd) cls += ' range-end';
              if(pickerStart && pickerEnd && k > pickerStart && k < pickerEnd) cls += ' in-range';
              return React.createElement('div',{key:i,className:cls,onClick:()=>handleDayClick(d)},d,data[k]&&React.createElement('div',{className:'day-dot'}));
            })
          ),
          React.createElement('div',{className:'cc-footer', style:{marginTop:'20px', padding: '0 20px 20px'}},
            React.createElement('button',{className:'cc-action secondary',onClick:()=>{setFilterStart('all');setFilterEnd('all');setShowPicker(false)}},'За весь час'),
            React.createElement('button',{className:'cc-action primary',onClick:()=>{setFilterStart(pickerStart);setFilterEnd(pickerEnd);setShowPicker(false)}},'Застосувати')
          )
        )
      )
    );
  }"""

# Use regex to replace the functions
js = re.sub(r'function renderBwPicker\(\)\{.*?(?=function renderCustomPicker)', bw_picker_new + '\n\n', js, flags=re.DOTALL)
js = re.sub(r'function renderCustomPicker\(\)\{.*?(?=\/\/ ─── MAIN RENDER)', custom_picker_new + '\n\n  ', js, flags=re.DOTALL)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Calendars synchronized")
