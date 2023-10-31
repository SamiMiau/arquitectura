import axios from "axios"


export async function command(text, user, user_id){
    if(text =="view inventory"){
        const inventory = await axios.get(`http://localhost:5003/inventory?user_id=${user_id}`)
        console.log(inventory.data)
        return ["Your inventory 📦", JSON.stringify(inventory.data)]
    }
    else if(text=="view shop"){
        const inventory = await axios.get(`http://localhost:5003/market`)
        console.log(inventory.data)
        return ["Shop 💰🛒", JSON.stringify(inventory.data)]
    }
    else{
        const command = text.split(" ")[0]
        const item_name = text.split(" ")[2]
        const quantity = text.split(" ")[3]
        if(command =="use"){
        
        }
        else if(command == "sell"){
        
        }
        else if(command == "buy"){
        
        }
    }


}