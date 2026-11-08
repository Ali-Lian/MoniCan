<template>
  <div id="app">
    <div class="header">
      <b-navbar toggleable type="dark" variant="dark">
        <b-navbar-brand href="#">MoniCan</b-navbar-brand>
      </b-navbar>
    </div>

    <div class="total_wrap">
      <div class="left_wrap" id="left_wrap">
        <Map :trashcan="trashcan" :record="record" :newRecord="newRecord" :community="community"/>
      </div>

      <div class="right_wrap">
        <div class="right_top">
          <b-table striped hover :items="items"></b-table>
        </div>
        <div class="right_down">
          <svg id="record">
          </svg> 
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Map from './components/Map.vue'
import FetchService from './FetchService';
import EventBus from './EventBus';
import * as d3 from "d3";
export default {
  name: 'App',
  components: {Map, FetchService, EventBus},
  data(){
    return {
      community: null,
      trashcan: null,
      record: null,
      newRecord: null,
      items: null,
      record_max_length: 0,
    }
  },
  mounted() {
    this.fetchData();
    EventBus.on('centerID', this.getSvgRecord);
    // (1) 抓取視窗是否縮放, 若有則重繪svg
    window.addEventListener('resize', ()=>{
      this.getSvgRecord();
    });
  },
  computed: {
    linePoints() {
      return this.record.map((data, index) => {
        const x = 50 + index * 20;
        const y = 350 - data.distance;
        return `${x},${y}`;
      }).join(' ');
    }
  },
  methods: {
    async fetchData() {
      try {
        this.community = await FetchService.getCommunity();
        this.trashcan = await FetchService.getTrashCan();
        this.record = await FetchService.getRecord();
        this.newRecord = await FetchService.getNewRecord();
        this.customer = await FetchService.getCostumer();
        this.filterCostumer();
        console.log(this.record)
      } catch(err) {
        this.error = err.message;
      }
    },
    filterCostumer(){
      // return this.customer;
      let items = [];
      if(this.customer != undefined){
        for(let i = 0; i < this.customer.length; ++i){
          let temp = {};
          temp.customerID = this.customer[i].customerID;
          temp.customerName = this.customer[i].customerName;
          temp.is_active = this.customer[i].is_active;
          for (let j = 0; j < this.community.length; j++) {
              let obj = this.community[j];
              if (obj.communityID == this.customer[i].communityID) {
                  temp.communityName = obj.communityName;
              }
          }
          items.push(temp);
        }
        this.items = items;
        return items;
      }
    },
    // 篩選出選中的marker的資料，用以篩選record繪圖
    getSvgRecord(event){
      let filterData  = null;
      let timeStamps = null;
      for(let i = 0; i < this.record.length; ++i){
        filterData = this.record.filter(record => record.trashCanID === i);
        if(filterData.length > this.record_max_length){
          this.record_max_length = filterData.length;
          timeStamps = filterData.map(d => d.timeStamp);
          console.log(filterData, timeStamps)
        }
      }
      filterData = this.record.filter(filterRecord => filterRecord.trashCanID == event);
      // console.log(filterData)
      const svg_obj = document.getElementById("record");
      if(d3.selectAll("svg#record path").size() == 0){
        // Set the dimensions and margins of the graph
        const margin = { top: 20, right: 0, bottom: 30, left: 80 },
              width =  svg_obj.clientWidth - margin.left - margin.right,
              height = svg_obj.clientHeight - margin.top - margin.bottom;
        // Append the svg object to the body of the page
        const svg = d3.select("#record")  // Append 'svg' as a string
                      .attr("width", width + margin.left + margin.right)
                      .attr("height", height + margin.top + margin.bottom)
                      .append("g");

        // Set the ranges
        // 提取所有的 timeStamp 值
        const maxWeight = d3.max(filterData, function(d) { return +d.weight; });
        const maxHeight = d3.max(filterData, function(d) { return +d.distance; });

        // 設定 y 軸比例尺
        const y = d3.scaleLinear()
            .domain([0, maxHeight])
            .range([height-margin.top-margin.bottom, 0]);

            svg.append("g")
              .call(d3.axisLeft(y))
              .attr("transform", `translate(${margin.left}, ${margin.top + 20})`);
        // 設定 y 軸比例尺
        const y2 = d3.scaleLinear()
            .domain([0, maxWeight])
            .range([height-margin.top-margin.bottom, 0]);

            svg.append("g")
              .call(d3.axisRight(y2))
              .attr("transform", `translate(${width-48}, ${margin.top + 20})`);

        // 設置 x 軸比例尺
        const x = d3.scaleOrdinal()
            .domain(timeStamps)
            .range(timeStamps.map((d, i) => i * ((width-margin.left - margin.right) / this.record_max_length)));
        
        // 繪製x軸
        svg.append("g")
            .attr("transform", `translate(${margin.left}, ${height - 10})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .style("font-size", "8px");

        // 定義線條
        const weightLine = d3.line()
            .x(d => x(d.timeStamp))
            .y(d => y2(d.weight));

        const distanceLine = d3.line()
            .x(d => x(d.timeStamp))
            .y(d => y(d.distance));

        // 添加 weight
        svg.append("path")
            .datum(filterData)
            .attr("stroke", "steelblue")
            .attr("fill", "none")
            .attr("id", "weight_path")
            .attr("d", weightLine)
            .attr("transform", `translate(${margin.left}, ${margin.top + 20})`);

        // 添加 distance
        svg.append("path")
            .datum(filterData)
            .attr("class", "line distance-line")
            .attr("stroke", "orange")
            .attr("fill", "none")
            .attr("id", "distance_path")
            .attr("d", distanceLine)
            .attr("transform", `translate(${margin.left}, ${margin.top + 20})`);

        // Add legend
        svg.append("text")
          .attr("x", width - 70)
          .attr("y", 30)
          .attr("class", "legend")
          .style("fill", "steelblue")
          .text("Weight");
        svg.append("text")
          .attr("x", width - 70)
          .attr("y", 50)
          .attr("class", "legend")
          .style("fill", "orange")
          .text("Distance");
        
        // Add dots
        svg.append('g')
          .selectAll("dot")
          .data(filterData)
          .join("circle")
              .attr("cx", function (d) { return x(d.timeStamp); } )
              .attr("cy", function (d) { return y2(d.weight); } )
              .attr("r", 3)
              .style("fill", "steelblue")
              .attr("class", "w_dot")
              .attr("transform", `translate(${margin.left}, ${margin.top + 20})`)
        
        // Add dots
        svg.append('g')
          .selectAll("dot")
          .data(filterData)
          .join("circle")
              .attr("cx", function (d) { return x(d.timeStamp); } )
              .attr("cy", function (d) { return y(d.distance); } )
              .attr("r", 3)
              .style("fill", "orange")
              .attr("class", "d_dot")
              .attr("transform", `translate(${margin.left}, ${margin.top + 20})`)
      }
      else{
        // console.log(filterData)
        const svg = d3.select("#record");
        svg.selectAll(".w_dot")
          .remove();
          svg.selectAll(".d_dot")
          .remove();
        // Set the dimensions and margins of the graph
        const margin = { top: 20, right: 0, bottom: 30, left: 80 },
              width =  svg_obj.clientWidth - margin.left - margin.right,
              height = svg_obj.clientHeight - margin.top - margin.bottom;

        // Set the ranges
        // 提取所有的 timeStamp 值
        const timeStamps = filterData.map(d => d.timeStamp);
        const maxWeight = d3.max(filterData, function(d) { return +d.weight; });
        const maxHeight = d3.max(filterData, function(d) { return +d.distance; });

        // 設定 y 軸比例尺
        const y = d3.scaleLinear()
            .domain([0, maxHeight])
            .range([height-margin.top-margin.bottom, 0]);
        // 設定 y 軸比例尺
        const y2 = d3.scaleLinear()
            .domain([0, maxWeight])
            .range([height-margin.top-margin.bottom, 0]);

        // 設置 x 軸比例尺
        const x = d3.scaleOrdinal()
            .domain(timeStamps)
            .range(timeStamps.map((d, i) => i * ((width-margin.left - margin.right) / this.record_max_length)));
        
        
        const weightLine = d3.line()
            .x(d => x(d.timeStamp))
            .y(d => y2(d.weight));

        const distanceLine = d3.line()
            .x(d => x(d.timeStamp))
            .y(d => y(d.distance));
        
        const temp_w = d3.select("#weight_path")
          .datum(filterData)
          .transition()
          .duration(500)
          .attr("d", weightLine);
        
        const temp_d = d3.select("#distance_path")
          .datum(filterData)
          .transition()
          .duration(500)
          .attr("d", distanceLine);
        
        // Add dots
        let temp_dot_w = svg.append('g')
          .selectAll("dot")
          .data(filterData)
          .join("circle")
              .attr("cx", function (d) { return x(d.timeStamp); } )
              .attr("cy", ((height + height -margin.top-margin.bottom)/2))
              .attr("r", 3)
              .style("fill", "steelblue")
              .attr("class", "w_dot")
              .attr("transform", `translate(${margin.left}, ${margin.top + 20})`)
        
        // Add dots
        let temp_dot_d = svg.append('g')
          .selectAll("dot")
          .data(filterData)
          .join("circle")
              .attr("cx", function (d) { return x(d.timeStamp); } )
              .attr("cy", ((height + height -margin.top-margin.bottom)/2))
              .attr("r", 3)
              .style("fill", "orange")
              .attr("class", "d_dot")
              .attr("transform", `translate(${margin.left}, ${margin.top + 20})`)
        
        temp_dot_d
          .data(filterData)
          .transition()
          .duration(500)
          .attr("cx", function (d) { return x(d.timeStamp); } )
          .attr("cy", function (d) { return y(d.distance); } );
        
        temp_dot_w
          .data(filterData)
          .transition()
          .duration(500)
          .attr("cx", function (d) { return x(d.timeStamp); } )
          .attr("cy", function (d) { return y2(d.weight); } );
      }
    },
  }
}
</script>

<style>
:root {
  --bs-navbar-padding-y: 0;
}
html, body{
  height: 100%;
  width: 100%;
}
#app {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}
.header{
  width: 100%;
  height: 8%;
  /* display: flex; */
  /* flex-direction: row; */
}
.navbar{
  width: 100%!important;
  height: 100%!important;
  padding: 0 0 0 1%!important;
  margin: 0!important;
}
.total_wrap{
  width: 100%;
  height: 92%;
  display: flex;
  flex-direction: row;
}
.left_wrap{
  width: 50%;
  height: 100%;
  padding: 1% 0.5% 1% 1%;
  /* box-shadow: 0px 0px 8px rgba(184, 184, 184, 0.9); */
  /* background-color: rgb(146, 228, 231); */
}

.right_wrap{
  width: 50%;
  height: 100%;
  padding: 1% 1% 1% 0.5%;
  display: flex;
  flex-direction: column;
  /* background-color: rgb(198, 170, 143); */
}
.right_top{
  width: 100%;
  height: 30%;
  overflow: auto;
  box-shadow: 0px 0px 8px rgba(184, 184, 184, 0.9);
}
.right_down{
  width: 100%;
  height: 70%;
  margin: 20px 0 0 0;
  box-shadow: 0px 0px 8px rgba(184, 184, 184, 0.9);
}
#record{
  width: 100%;
  height: 100%;
}
</style>
