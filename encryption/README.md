# If there's one fundamental part of every FinTech application, it's security.

With Eaze, there's an obvious major security issue - what if I can pay someone elses face?

We solved that problem in both a preventative and reactive way - preventative as the user needs to be facing the camera and have their eyes closed for more than 3 seconds to verify the payment, and in a reactive way, as users receive a notification each time a transaction is made with their Eaze account, and if the transaction wasn't made by them, they can temporarily lock their Eaze account.

Ultimately, the misuse of Eaze POS's is down to the individual businesses themselves. As each POS is uniquely tied to a single businesses, if a single POS has high rates of fraud, that means the owner is not doing a good job of ensuring that people aren't misusing the POS, or perhaps the owner is a criminal himself. As the POS takes pictures, it can also help in determining the guilty party in case of fraud.


---------------------------

However, another problem arises - how can we ensure we are only receiving requests from certified POS's? Without the digital signatures and encryption that were applied here, it would be relatively easy for someone to create their own untrackable POS and use it to steal people's money. Digital signatures ensure that only POS's that Eaze issued will be considered by the server.

This folder is present on each POS, with each POS having a different public/private key pair and ID.
