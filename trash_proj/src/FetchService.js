import axios from 'axios';

const url_community = 'http://localhost:3000/community';
const url_TrashCan = 'http://localhost:3000/TrashCan';
const url_Record = 'http://localhost:3000/Record';
const url_newRecord = 'http://localhost:3000/newRecord';
const url_customer = 'http://localhost:3000/customer';

class FetchService{
    // Get community, 讀取專案資料
    static getCommunity(){
        return new  Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url_community);
                const data = res.data;
                resolve(
                    // resolve會回傳複製後的結果且不會影響到讀入的data
                    data.map(obj_data =>({
                        ...obj_data,
                    }))
                )
            } catch(err) {
                reject(err);
            }
        });
    }

    static getTrashCan(){
        return new  Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url_TrashCan);
                const data = res.data;
                resolve(
                    // resolve會回傳複製後的結果且不會影響到讀入的data
                    data.map(obj_data =>({
                        ...obj_data,
                    }))
                )
            } catch(err) {
                reject(err);
            }
        });
    }

    static getRecord(){
        return new  Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url_Record);
                const data = res.data;
                resolve(
                    // resolve會回傳複製後的結果且不會影響到讀入的data
                    data.map(obj_data =>({
                        ...obj_data,
                    }))
                )
            } catch(err) {
                reject(err);
            }
        });
    }

    static getNewRecord(){
        return new  Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url_Record);
                const data = res.data;
                resolve(
                    // resolve會回傳複製後的結果且不會影響到讀入的data
                    data.map(obj_data =>({
                        ...obj_data,
                    }))
                )
            } catch(err) {
                reject(err);
            }
        });
    }

    static getCostumer(){
        return new  Promise(async (resolve, reject) => {
            try {
                const res = await axios.get(url_customer);
                const data = res.data;
                resolve(
                    // resolve會回傳複製後的結果且不會影響到讀入的data
                    data.map(obj_data =>({
                        ...obj_data,
                    }))
                )
            } catch(err) {
                reject(err);
            }
        });
    }
}



export default FetchService;
