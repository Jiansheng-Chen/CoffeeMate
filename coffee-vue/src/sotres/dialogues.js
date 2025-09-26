import {defineStore} from 'pinia'
import {ref} from 'vue'



export const useDialoguesStore = defineStore('dialogues',()=>{
    const dialogues = ref([])
    function setDialogue(list){
            dialogues.value = list
        }
    function getDialogue(){
            return dialogues.value
        }
    function addDialogue(item){
            const dialogue = dialogues.value.find(d => d.id == item.id)
            //console.log('addDialogue find result', dialogue)
            if (dialogue != null) {
                //console.log("addDialogue true")
                //console.log("addDialogue before", dialogues.value)
                dialogue.history=item.history
                //console.log("addDialogue after", dialogues.value)
            }
            else{
                //console.log("addDialogue false")
                //console.log("addDialogue before", dialogues.value)
                dialogues.value.push(item)
                //console.log("addDialogue after", dialogues.value)
            }
            
        }
    function appendHistoryById(messages,id){
            const dialogue = dialogues.value.find(d => d.id === id)
            console.log("appendHistoryById:", messages, id)
            console.log("appendHistoryById: dialogue", dialogue)
            console.log("appendHistoryById: .history", dialogue.history)
            dialogue.history.push(...messages)
        }

    function findDialogueById(id){
            console.log(`findDialogueById:${id}`)
            const dialogue = dialogues.value.find(d => d.id === id)
            console.log('findDialogueById result,', dialogue)
            if(Array.isArray(dialogue.history) && dialogue.history.length != 0){
                //console.log(`findDialogueById:${id} history is not empty`)
                return dialogue
                
            }
            else{
                //console.log(`findDialogueById:${id} history is empty`)
                //console.log(`findDialogueById ${dialogue}`)
                console.warn(`pinia中未找到id为${id}的历史`)
                return null
            }
        }

    function clear(){
            dialogues.value=[]
        }
    
    return {dialogues, setDialogue, getDialogue, addDialogue, appendHistoryById, findDialogueById, clear} 
})



// export const useDialoguesStore = defineStore('dialogues', {
//     state:()=>({
//         dialogues : [],
//     }),

//     getters:{
//         dialogueCount(state){
//             return state.dialogues.length
//         },

        
//     },

//     actions:{
//         setDialogue(list){
//             this.dialogues = list
//         },
//         getDialogue(){
//             return this.dialogues
//         },
//         addDialogue(item){
//             this.dialogues.push(item)
//         },

//         appendHistoryById(messages,id){
//             const dialogue = this.dialogues.find(d => d.id === id)
//             dialogue.history.push(...messages)
//         },

//         findDialogueById(id){
//             const dialogue = this.dialogues.find(d => d.id === id)
//             if(!dialogue){
//                 console.warn(`未找到id为${id}的对话`)
//                 return null
//             }
//             else{
//                 return dialogue
//             }
//         },

//         clear(){
//             this.dialogues=[]
//         }
//     }


// })

