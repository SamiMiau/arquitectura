import axios from "axios"


export async function command(text, user, user_name){
    let user_id2 = await axios.get(`http://localhost:5003/getuserid/${user_name}`)
    let user_id = user_id2.data
    if(text ==="sign in"){
        
    }
    else if(text ==="view inventory"){
        const inventory = await axios.get(`http://localhost:5003/inventory?user_id=${user_id}`)
        console.log(inventory.data)
        return ["Your inventory 📦", inventory.data]
    }
    else if(text==="view shop"){
        const inventory = await axios.get(`http://localhost:5003/market`)
        console.log(inventory.data)
        return ["Shop 💰🛒", JSON.stringify(inventory.data)]
    }
    else if(command==="view plants"){
        console.log("view plantsss")
        const inventory = await axios.get(`http://localhost:5001/plants`) //lista de diccionarios, donde cada diccionario es un usuario
        console.log(inventory.data)
        return ["Plants available 🍉", "inventory.data"]
    }
    
    else{
        const command = text.split(" ")[0]
        const item_name = text.split(" ")[2]
        const quantity = text.split(" ")[3]
        if(command ==="use"){
            
        }
        else if(command === "sell"){
            const inventory = await axios.post(`http://localhost:5003/sell/${user_id}/${item_name}/${quantity}`)
            console.log(inventory.data)
            //atrapar error de no se pudo completar
            if(inventory.data === 0){
                return ["Not enough items to sell 😭", ""]
            }
            else if(inventory.data === 1){
                return ["Sale completed 😎💹", ""]
            }
        }
        else if(command === "buy"){
            const inventory = await axios.post(`http://localhost:5003/buy/${user_id}/${item_name}/${quantity}`)
            console.log(inventory.data)
            //atrapar error de no se pudo completar
            if(inventory.data === 0){
                return ["Not enough gold 😭", " "]
            }
            else if(inventory.data === 1){
                return ["Purchase completed 😎", " "]
            }
        }
        else if(command==="login"){
            const inventory = await axios.get(`http://localhost:5000/users`) //lista de diccionarios, donde cada diccionario es un usuario
            let inven = inventory.data
            for(let i = 0; i < inven.length; i++){
                if(inven[i]["username"]===item_name){
                    if(inven[i]["password"]===quantity){
                        return ["Logged in ✅", item_name]
                    }
                    else{
                        return ["Can not log in ❌", item_name]
                    }
                }
              }
            console.log(inventory.data)
        }
        
    }


}