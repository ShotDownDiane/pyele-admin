let eOAuth = function (authorizedAddress, successCallback) {
    return {
        data: {
            access_token: '',
            expires_in: null,
            refresh_token: '',
            token_type: ''
        },
        get_state() {
            return localStorage.getItem('oauth-state')
        },
        get_data() {
            return JSON.parse(localStorage.getItem('oauth-token'))
        },
        checkAuth() {
            if (!this.get_state()) {
                this.jumpAuth()
            }
            return this
        },
        reset() {
            localStorage.removeItem('oauth-state')
            localStorage.removeItem('oauth-token')
            return this
        },
        jumpAuth(reset = true) {
            let t = setInterval(() => {
                if (this.get_state()) {
                    this.data = this.get_data()
                    clearInterval(t)
                    successCallback && successCallback(this.data)
                    reset && setTimeout(() => {
                        this.reset()
                    }, 1000)
                }
            }, 500)
            window.open(authorizedAddress);
        }
    }
}