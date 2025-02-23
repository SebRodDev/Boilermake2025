import React, { useEffect } from 'react';

export default function Login() {
    useEffect(() => {
        /* global google */
        google.accounts.id.initialize({
            client_id: '972643943324-42ks2gp1k1qkhjpodnbi4jnl5qil4osu.apps.googleusercontent.com',
            callback: handleCredentialResponse
        });
        google.accounts.id.renderButton(
            document.getElementById('googleSignInButton'),
            { theme: 'outline', size: 'large' }
        );
    }, []);

    const handleCredentialResponse = (response) => {
        console.log('Encoded JWT ID token: ' + response.credential);
        // You can send the token to your server for verification and further processing
    };

    return (
        <div>
            <h1>APP NAME</h1>
            <h2>Create an account</h2>
            <h3>Enter your email to signup</h3>
            <input type="email" placeholder="email@domain.com" />
            <button>Sign up with email</button>
            <p>---------or continue with---------</p>
            <div id="googleSignInButton"></div>
            <a>By clicking continue, you agree to our Terms of Service and Privacy Policy</a>
        </div>
    );
}