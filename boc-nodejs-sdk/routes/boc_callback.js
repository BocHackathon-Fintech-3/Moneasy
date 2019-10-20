var router = require('express').Router();

function boc_callback_handler(req,res,next){
    console.log("back")
    if(req.query.code){
        console.log("back")
        // res.send("Success! I am not able to execute actions on your behalf")

        boc_api.getOAuthCode2(req.query.code).then(oauthcode2 =>{         
            boc_api.getSubIdInfo(boc_api.sub_id,oauthcode2.access_token).then(subscription_info =>{
                boc_api.updateSubId(boc_api.sub_id,oauthcode2.access_token,subscription_info[0].selectedAccounts).then(sub_info =>{
                    boc_api.subStatus = sub_info;
                    boc_api.cacheApiObject()
                    res.redirect('/')
                }).catch(error=>console.log(error))
            }).catch(error=>console.log(error))
        }).catch(error=>console.log(error))
    }
}

router.get('/',boc_callback_handler)

module.exports = router;