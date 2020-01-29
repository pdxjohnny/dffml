import React from 'react';
import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import Paperbase from './Paperbase';
import theme from './theme';

import DemoServer from './DemoServer';

var demoServer = new DemoServer();
demoServer.start();

ReactDOM.render(
  <ThemeProvider theme={theme}>
    {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
    <CssBaseline />
    <Paperbase demoServer={demoServer} />
  </ThemeProvider>,
  document.querySelector('#root'),
);
