<template>
  <div id="map_wrap">
    <!-- title="子母車地圖" sub-title="Card subtitle" -->
    <!-- <b-card class="map_wrap"> -->
        <!-- 地圖區域 -->
        <l-map  class="map" :zoom="zoom" :center="center" id="lmap" :max-bounds="maxBounds" ref="myMap" >
          <!--底圖圖層-->
          <l-tile-layer :url="url" :attribution="attribution"></l-tile-layer>
          
          <l-layer-group>
            <l-marker  v-for="item in trashcan" :lat-lng="[item.lat, item.lng]" :key="item.trashCanID" @click="changeCenter($event, item.trashCanID)">
              <l-icon>
                <svg :fill="changeMarkerColor(item.trashCanID)" width="19px" height="22px" :id="'can' + item.trashCanID" >
                  <defs>
                    <filter id="shadow" width="120" height="120">
                      <feOffset in="SourceAlpha" dx="20" dy="20" />
                      <feGaussianBlur stdDeviation="10" />
                      <feBlend in="SourceGraphic" in2="blurOut" />
                    </filter>
                  </defs>
                  <g>
                    <path d="M516.316,337.52l94.233,193.581    
                      M444.541,205.228c0,105.776-88.058,125.614-129.472,227.265
                      c-3.365,8.26-14.994,8.218-18.36-0.04c-37.359-91.651-112.638-116.784-127.041-198.432
                      c-14.181-80.379,41.471-159.115,122.729-166.796C375.037,59.413,444.541,124.204,444.541,205.228z M379.114,205.228
                      c0-40.436-32.779-73.216-73.216-73.216s-73.216,32.78-73.216,73.216c0,40.437,32.779,73.216,73.216,73.216
                      S379.114,245.665,379.114,205.228z" style=" transform: translate(-8.5px, -3px) scale(0.053)" :filter="addShadow(item.trashCanID)" />
                  </g>
                </svg>
                <!-- <img src="../assets/marker_2.svg" alt="ubikes" class="can" :id="item.trashCanID" :style="{fill: 'red' }" > -->
              </l-icon>
              <l-popup>垃圾桶編號：{{item.trashCanID}} <br> 社區名稱： {{getCommunityName(item.communityID)}} <br> 
                        目前垃圾量: {{ Math.ceil(((100 - newRecord[item.trashCanID].distance) / 100) * 100) }}%
              </l-popup>
            </l-marker>
          </l-layer-group>
        </l-map>
    <!-- </b-card> -->
  </div>
</template>

<script>
import {latLngBounds, latLng} from "leaflet";
import {LMap, LTileLayer, LMarker, LIcon, LPopup} from 'vue2-leaflet';
import "leaflet/dist/leaflet.css";
import EventBus from '../EventBus';
import * as d3 from "d3";
export default {
  name: 'Map',
  components: { LMap, LTileLayer, LMarker, LIcon, LPopup, EventBus},
  props:['trashcan', 'record', 'newRecord', 'community'],
  data () {
    return {
      // ?api_key=f3a6e7c7-9380-4bbb-a873-83ca83197b9e
      url: 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png?api_key=f3a6e7c7-9380-4bbb-a873-83ca83197b9e',
      attribution:
        '&&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
      zoom: 15,//初始縮放比例
      center: [22.621724001099924, 120.2713018174192],// 地圖中心點
      push: false,//判斷使用者是否要新增選取地點
      newCircleDetails:[],//紀錄使用者選去地點與範圍資料
      maxBounds: latLngBounds([// 設定地圖邊界
        [22.229573497276068, 119.66995239257814],
        [22.901501217049034, 120.8280395507814]
      ]),
      centerID: null, // 紀錄center的id
      // interpolateColor: d3.interpolate("#4e79a7", "#e15759"),
      // interpolateColor: d3.scaleSequential(d3.interpolateRdBu),
    };
  },
  created() {
  },
  mounted(){
  },
  methods:{
    // 計算容量並更改marker顏色
    changeMarkerColor(canID){
      // 遍歷垃圾桶data
      const interpolateColor = d3.interpolateHcl("#FF5151", "#00AEAE");
      return interpolateColor((this.newRecord[canID].distance) / 100);
    },
    // 改變中心
    changeCenter(event, tempCenter){
      this.center = event.latlng;
      this.centerID = tempCenter;
      EventBus.emit('centerID', this.centerID);
      // console.log(event)
    },
    // 用來顯示tooltip的社區名稱
    getCommunityName(communityID) {
      const community = this.community.find(c => c.communityID === communityID);
      return community ? community.communityName : '未知社區';
    },
    // 選中的marker加陰影
    addShadow(tempCenter){
      if(tempCenter == this.centerID && this.centerID != null){
        return "url(#shadow)";
      }else{
        return "url(#none)";
      }
    }
  }
}
</script>

<style>
#map_wrap{
    width: 100%;
    height: 100%;
    box-shadow: 0px 0px 8px rgba(184, 184, 184, 0.9);
    /* position: relative; */
}
.can{
  width: 150%;
  height: 150%;
}
#lmap{
  position: relative;
  width: 100%;
  height: 87.5vh;

}
</style>
  