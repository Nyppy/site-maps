import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

declare var ymaps:any;

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {
  public map :any;

  value_tab = [];
  response: any;
  id = 0;
  temp_i = 0;

  trrr = [[], [],
          [], [],
          [], [],
          [], [],
          [], []];

  a: any;
  b: any;
  c: any;
  d: any;
  myMap: any;
  zoom_1 = 5;
  center = [55.76, 37.64]

  constructor(private http: HttpClient){}

  ngOnInit() {
    ymaps.ready().then(() => {
      this.myMap = new ymaps.Map('map', {
        // center: [55.76, 37.64],
        center: this.center,
        zoom: this.zoom_1
      }, {
        searchControlProvider: 'yandex#search'
      });
    });
  }

  path_value(i) {
    this.id = i;
    this.myMap.geoObjects
      .add(new ymaps.Placemark([Number(this.trrr[this.id][1]), Number(this.trrr[this.id][2])], {
          balloonContent: this.trrr[i][0]
      }, {
          preset: 'islands#icon',
          iconColor: '#0095b6'
      }));
    console.log(this.id)
    return this.id;
  }

  get_data(i) {
    const city = {'city': this.value_tab[i]};
    console.log(city)
    this.http.post('http://127.0.0.1:5000/api/v1.0/city', city)
    .subscribe((response)=>{
      this.response = response;
      this.trrr[i].push(this.response.d, this.response.h, this.response.p, this.response.p1);
    })
  }

  // выводит окно для ввода города и записывает его в массив +
  // проверяет количество введенных городов
  target_data() {
    let v = prompt('Введите город');
    if(this.value_tab.length != 10 && v.length >= 1) {
      this.value_tab.push(v);
      for (let i = 0; i < this.trrr.length; i++) {
        if (this.trrr[i].length < 1) {
          this.trrr[i].push(v)
          break;
        } else {
          continue;
        }
      }
    } else {
      alert('Введено предельно допустимое количество объектов');
    }
  }

  del_data(id) {
    var city_del = {'sity': this.value_tab[id] };
    var del_new_arr = [];
    const new_tr = [[], [],
                    [], [],
                    [], [],
                    [], [],
                    [], []];

    this.trrr[id] = [];
    let ii = 0
    for (let i = 0; i < this.trrr.length; i++) {
        if (this.trrr[i].length == 1) {
          new_tr[ii].push(this.trrr[i])
          ii++;
        } else if (this.trrr[i].length == 5) {
          new_tr[ii].push(this.trrr[i][0],  this.trrr[i][1], this.trrr[i][2], this.trrr[i][3], this.trrr[i][4])
          ii++;
        }
    }

    this.trrr = new_tr;

    this.http.post('http://127.0.0.1:5000/api/v1.0/city/del', city_del)
    .subscribe((response)=>{
      this.response = response;
      for (let i = 0; i < this.response.s.length; i++) {
        if (new_tr[i][0] == this.response.s[i]) {
          new_tr[i].push(this.response.d[i], this.response.h[i], this.response.p[i], this.response.p1[i]);
        }
      }
    })
    this.trrr = new_tr;

    this.myMap.geoObjects.removeAll()
  }

  show_data() {
    console.log(this.trrr[0].length)
    var t = 0;
    var j1 = 0;
    var j2 = 0;
    for (let i = 0; i < this.trrr.length; i++) {
      if (this.trrr[i].length > 1) {
        t = 1;
        break;
      } else {
       alert('Объектов нет!');
       t = 0;
       break;
      }
    }

    if (t == 1) {
      for (let i = 0; i < this.trrr.length; i++) {
        if (this.trrr[i].length > 1) {
          this.myMap.geoObjects
            .add(new ymaps.Placemark([Number(this.trrr[i][1]), Number(this.trrr[i][2])], {
                balloonContent: this.trrr[i][0]
            }, {
                preset: 'islands#icon',
                iconColor: '#0095b6'
            }));
        }
      }
    }
    var tt = 0
    for (let i = 0; i < this.trrr.length; i++) {
      if (this.trrr[i].length > 2) {
        tt += 1;
      }
    }
    if (tt > 2) {
      j1 = this.trrr[0][1] - this.trrr[1][1];
      j2 = this.trrr[0][2] - this.trrr[1][2];
      this.zoom_1 += 1
    }
    const yt = [this.trrr[0][1]-j1, this.trrr[0][2]-j2];

    this.center = yt;
  }
}
