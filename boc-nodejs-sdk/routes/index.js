var router = require('express').Router();


router.get('/', function (req, res, next) {
    if (boc_api) {
        res.render('index', {
            boc_api: boc_api
        });
    } else {
        res.status(500).send('BoC SDK not initialized')
    }
    // if(boc_api && boc_api.subStatus.status === "ACTV" && boc_api.subStatus.selectedAccounts.length > 0){
    //     res.send(JSON.stringify(boc_api))
    // }else{
    //     res.send("<a href='"+boc_api.get_login_url()+"'>Connect a BOC Account</a>");
    // }

})

router.get("/getAccountsInSub", function (req, res, next) {
    if (req.query.accountId) {
        boc_api.getSubForAccount(req.query.accountId).then(subForAccount => {
            // res.render('accounts', {
            //     subForAccount: subForAccount
            // })
            res.send(subForAccount)
        })
    } else {
        res.status(400)
        res.render('error', {
            error: 'missing information',
        })
    }

})

router.get('/account/fundAvailability', function (req, res, next) {
    if (req.query.accountId) {
        boc_api.fundAvailability(req.query.accountId).then(response => {
            res.send(response)
        })
    } else {
        res.status(400)
        res.render('error', {
            error: 'missing information',
        })
    }

})

router.get('/accounts/:accountid/statements', function (req, res, next) {
    var account_id = req.params.accountid;
    boc_api.getAccountStatements(account_id).then(accountStatements => {
        res.render('statements', {
            statements: accountStatements
        })
        // res.send(accountStatements)
    })

})

router.get('/accounts/:accountid/balances', function (req, res, next) {
    var account_id = req.params.accountid;
    boc_api.getAvailBalanceForAccount(account_id).then(accountBalance => {
        res.render('balances', {
            account: accountBalance[0]
        })
        // res.send(accountBalance)
    })

})

router.get('/accounts', function (req, res, next) {
    boc_api.getAccounts(function (err, data) {
        if (err) {
            res.send(err)
        } else {
            //res.send(data)
            res_obj = []
            data.forEach(account => {
                boc_api.getAccount(account.accountId, function (err, accountData) {
                    if (err) {
                        throw err;
                    } else {

                        res_obj.push(accountData);
                    }

                    if (res_obj.length === data.length) {
                        res.render('accounts', {
                            accounts: res_obj
                        })
                        // res.send(res_obj);
                    }
                })
            });
        }
    })
})

router.get('/accounts/:accountid', function (req, res, next) {
    var account_id = req.params.accountid;
    boc_api.getAccount(account_id, function (err1, accountData) {
        boc_api.getAccountPayments(account_id, function (err2, paymentList) {
            var obj = {
                paymentlist: paymentList
            }
            console.log(accountData)
            if (!accountData.fatalError) {
                res.render('account', {
                    account: Object.assign(obj, accountData[0])
                })
            } else {
                res.status(500)
                res.render('error', {
                    error: 'Account ID is invalid',
                })
            }

            // res.send(Object.assign(obj, accountData[0]))
        })
    })

})

router.get("/payment/:paymentId", function (req, res, next) {
    var payment_id = req.params.paymentId;
    boc_api.getPaymentDetails(payment_id).then(paymentDetails => {
        if((typeof paymentDetails.status === "undefined")){
            res.status(400)
            res.render('error', {
                error: 'Invalid payment ID',
            })
        }
        else{
            res.render('payment', {
                payment: paymentDetails
            })
        }
    })
})

router.get('/pay', function (req, res, next) {
    if (req.query.creditorIban && req.query.debtorIban && req.query.amount) {
        const creditorIban = req.query.creditorIban
        const debtorIban = req.query.debtorIban
        const amount = req.query.amount

        if(creditorIban == debtorIban){
            res.status(400)
            res.render('error', {
                error: 'Please verify creditor and debtor account IDs are correct',
            })
        }
        else{
        boc_api.signPaymentRequest(creditorIban, debtorIban, amount, "SDK test payment", function (err, data) {
            if (err) {
                res.send(err)
            } else {
                //res.send(data)
                boc_api.createPayment(data, function (err, paymentResult) {
                    if (err) {
                        res.send(err)
                    } else {
                        if((typeof paymentResult.payment === "undefined")){
                            res.status(400)
                            res.render('error', {
                                error: 'Please verify creditor and debtor account IDs are correct',
                            })
                        }
                        else{
                        console.log(paymentResult.payment.paymentId)
                        boc_api.approvePayment(paymentResult.payment.paymentId, function (err, paymentAuthorizeResult) {
                            if (err) {
                                res.send(err)
                            } else {
                                res.render('pay', {
                                    result: paymentAuthorizeResult,
                                    paymentId: paymentResult.payment.paymentId
                                })
                                // res.send(paymentAuthorizeResult)
                            }
                        })
                    }
                    }
                })
            }
        })
    }

        /*
        var payload = {
            "debtor": {
              "bankId": "",
              "accountId": "351012345671"
            },
            "creditor": {
              "bankId": "",
              "accountId": "351092345672"
            },
            "transactionAmount": {
              "amount": 666,
              "currency": "EUR",
              "currencyRate": "string"
            },
            "endToEndId": "string",
            "paymentDetails": "yolo",
            "terminalId": "string",
            "branch": "",
             "executionDate": "",
            "valueDate": ""
          }
          
        boc_api.signPaymentRequest(payload,function(err,data){
            if(err){
                res.send(err)
            }else{
                boc_api.createPayment(data,function(err,paymentResult){
                    if(err){res.send(err)}
                    else{
                        
                        boc_api.approvePayment(paymentResult.payment.paymentId,function(err,paymentAuthorizeResult){
                            if(err){res.send(err)}
                            else{
                                res.send(paymentAuthorizeResult)
                            }
                        })
                    }
                })
            }
        })*/


    } else {
        res.status(400)
        res.render('error', {
            error: 'missing information',
        })
    }

})

router.get('/payFace', function (req, res, next) {
    if (req.query.creditorIban && req.query.debtorIban && req.query.amount && req.query.subId) {
        const creditorIban = req.query.creditorIban
        const debtorIban = req.query.debtorIban
        const amount = req.query.amount

        if(creditorIban == debtorIban){
            res.send("wrong")
        }
        else{
            boc_api.sub_id = req.query.subId
            boc_api.signPaymentRequest(creditorIban, debtorIban, amount, "SDK test payment", function (err, data) {
            if (err) {
                res.send(err)
            } else {
                //res.send(data)
                boc_api.createPayment(data, function (err, paymentResult) {
                    if (err) {
                        res.send(err)
                    } else {
                        if((typeof paymentResult.payment === "undefined")){
                            res.send("wrong")
                        }
                        else{
                        console.log(paymentResult.payment.paymentId)
                        boc_api.approvePayment(paymentResult.payment.paymentId, function (err, paymentAuthorizeResult) {
                            if (err) {
                                res.send(err)
                            } else {
                                res.send("Complete");
                                // res.send(paymentAuthorizeResult)
                            }
                        })
                    }
                    }
                })
            }
        })
    }
    } else {
        res.send("missing info")
    }

})


router.get('/getToken', function (req, res, next) {
        var data = {
            "client_id": boc_api.client_id,
            "client_secret": boc_api.client_secret,
            "grant_type":"client_credentials",
            "scope":"TPPOAuth2Security"
        }
        boc_api.post("/oauth2/token", data,null,function(error, response, body) {
            if (error) {
                res.send("error")
                    reject(error);

            } else {
                
                token_response = JSON.parse(body)
                if(token_response.access_token){
                    console.log("[Got Token]")
                    res.send(token_response.access_token)                        
                }else{
                    res.send('wee')                        
                    reject(token_response,null)
                }
            }
        })   
})

router.get('/getSub', function (req, res, next) {
            var data = {
                "accounts": {
                    "transactionHistory": true,
                    "balance": true,
                    "details": true,
                    "checkFundsAvailability": true
                },
                "payments": {
                    "limit": 99999999,
                    "currency": "EUR",
                    "amount": 999999999
                }
            }
            var headers = {
                "Authorization":"Bearer "+req.query.access_token,
                "Content-Type":"application/json",
                "app_name":"myapp",
                "tppid": boc_api.tppid,
                "originUserId":"abc",
                "timeStamp":Date.now(),
                "journeyId":"abc"
            }
            var url = "/v1/subscriptions?client_id="+boc_api.client_id+"&client_secret="+boc_api.client_secret
            boc_api.post(url,data,headers,function(err,response,body){
                if(err){
                    res.send('err')
                    reject(err)
                }else{
                    subBody = body
                    sub_Id = subBody.subscriptionId
                    console.log("[GOT SUB_ID]")
                    res.send(boc_api.get_login_url(sub_Id))
                }
            })
    })


router.get('/secondAuth', function (req, res, next) {
        var data = {
            "client_id":boc_api.client_id,
            "client_secret":boc_api.client_secret,
            "grant_type":"authorization_code",
            "scope":"UserOAuth2Security",
            "code":req.query.code
        }
        boc_api.post("/oauth2/token",data,null,function(err,response,body){
            if(err){
                reject(err)
                res.send('err')
            }
            console.log(body)
            oauthcode2 = JSON.parse(body)
            console.log("[GOT User Approval Code]")
        })

        var url = "/v1/subscriptions/"+req.query.subId+"?client_id="+boc_api.client_id+"&client_secret="+boc_api.client_secret;
        var headers = {
            "Authorization":"Bearer "+req.query.access_token,
            "Content-Type":"application/json",
            "originUserId":"abc",
            "tppId":boc_api.tppid,
            "timestamp":Date.now(),
            "journeyId":"abc"
        }
        boc_api.get(url,headers,function(err,response,body){
            if(err){
                reject(err);
            }
            subscription_info = JSON.parse(body)

        var data = {
            "selectedAccounts": subscription_info[0].selectedAccounts,
            "accounts": {
                "transactionHistory": true,
                "balance": true,
                "details": true,
                "checkFundsAvailability": true
            },
            "payments": {
                "limit": 8.64181767,
                "currency": "EUR",
                "amount": 93.21948702
            }
        }
        var headers= {
            "Authorization":"Bearer "+oauthcode2,
            "Content-Type":"application/json",
            "app_name":"myapp",
            "tppid":boc_api.tppid,
            "originUserId":"abc",
            "timeStamp":Date.now(),
            "journeyId":"abc"
        }
        
        var url = "/v1/subscriptions/"+req.query.subId+"?client_id="+boc_api.client_id+"&client_secret="+boc_api.client_secret;
        boc_api.patch(url,data,headers,function(err,response,body){
            if(err){
                reject(err)
            }else{
                res.send(subscription_info[0])
            }
        })
    })
})

module.exports = router;