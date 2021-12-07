import React from 'react';
import '../style/Loading.css';

function Loading() {
    return (
        <div class="container">
            <div class="lds-ripple">
                <div></div>
                <div></div>
            </div>
        </div>
    );
}

export default Loading;
