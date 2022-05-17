import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Button } from '@mui/material';
import { Auth } from 'aws-amplify';
import logo from './logo.png';
import './navbar.css';

function NavBar() {
    return (
        <div style={{ flexGrow: 1 }}>
            <AppBar position="static" color="primary">
                <Toolbar>
                    <div className="topBarLogoContainer">
                        <img src={logo} alt="Logo" />
                    </div>
                    <Typography variant="h5" color="inherit" style={{ flexGrow: 1 }}>
                        TRE Secure Data Egress
                    </Typography>
                    <div slot="amplify-sign-out">
                        <Button color="warning" variant="contained" onClick={() => Auth.signOut()}>
                            Sign Out
                        </Button>
                    </div>
                </Toolbar>
            </AppBar>
        </div>
    );
}
export default NavBar;
