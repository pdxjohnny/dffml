import React from 'react';
import PropTypes from 'prop-types';
import { createMuiTheme, ThemeProvider, withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Hidden from '@material-ui/core/Hidden';
import Navigator from './Navigator';
import Header from './Header';
import {
  HashRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";

import SetBackendPopup from './SetBackendPopup';
import SourcesUpload from './SourcesUpload';
import SettingsBackend from './SettingsBackend';
import NotFound from './NotFound';

let theme = createMuiTheme({
  palette: {
    primary: {
      light: '#63ccff',
      main: '#009be5',
      dark: '#006db3',
    },
  },
  typography: {
    h5: {
      fontWeight: 500,
      fontSize: 26,
      letterSpacing: 0.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  props: {
    MuiTab: {
      disableRipple: true,
    },
  },
  mixins: {
    toolbar: {
      minHeight: 48,
    },
  },
});

theme = {
  ...theme,
  overrides: {
    MuiDrawer: {
      paper: {
        backgroundColor: '#18202c',
      },
    },
    MuiButton: {
      label: {
        textTransform: 'none',
      },
      contained: {
        boxShadow: 'none',
        '&:active': {
          boxShadow: 'none',
        },
      },
    },
    MuiTabs: {
      root: {
        marginLeft: theme.spacing(1),
      },
      indicator: {
        height: 3,
        borderTopLeftRadius: 3,
        borderTopRightRadius: 3,
        backgroundColor: theme.palette.common.white,
      },
    },
    MuiTab: {
      root: {
        textTransform: 'none',
        margin: '0 16px',
        minWidth: 0,
        padding: 0,
        [theme.breakpoints.up('md')]: {
          padding: 0,
          minWidth: 0,
        },
      },
    },
    MuiIconButton: {
      root: {
        padding: theme.spacing(1),
      },
    },
    MuiTooltip: {
      tooltip: {
        borderRadius: 4,
      },
    },
    MuiDivider: {
      root: {
        backgroundColor: '#404854',
      },
    },
    MuiListItemText: {
      primary: {
        fontWeight: theme.typography.fontWeightMedium,
      },
    },
    MuiListItemIcon: {
      root: {
        color: 'inherit',
        marginRight: 0,
        '& svg': {
          fontSize: 20,
        },
      },
    },
    MuiAvatar: {
      root: {
        width: 32,
        height: 32,
      },
    },
  },
};

const drawerWidth = 256;

const styles = {
  root: {
    display: 'flex',
    minHeight: '100vh',
  },
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  app: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  main: {
    flex: 1,
    padding: theme.spacing(6, 4),
    background: '#eaeff1',
  },
  footer: {
    padding: theme.spacing(2),
    background: '#eaeff1',
  },
};

const DEFAULT_VIEW_ROUTE = "sources/upload";

var backend_url_initial = localStorage.getItem('backend.url');

if (backend_url_initial === null || backend_url_initial === "demo") {
  backend_url_initial = "/api";
}

const BACKEND_DEFAULT = {
  url: backend_url_initial,
};

function Paperbase(props) {
  const { classes, demoServer } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [backend, setBackend] = React.useState(BACKEND_DEFAULT);

  async function saveBackend(backend_url) {
    localStorage.setItem('backend.url', backend_url);

    if (backend_url === null || backend_url === "demo") {
      backend_url = "/api";
      demoServer.start();
    } else {
      demoServer.stop();
    }
    var backend = {
      url: backend_url,
    }
    setBackend(backend);
    return backend;
  }

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <div className={classes.root}>
          <CssBaseline />
          <SetBackendPopup
            open={localStorage.getItem('backend.url') === null}
            backend={backend}
            saveBackend={saveBackend}
          />
          <nav className={classes.drawer}>
            <Hidden smUp implementation="js">
              <Navigator
                PaperProps={{ style: { width: drawerWidth } }}
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
              />
            </Hidden>
            <Hidden xsDown implementation="css">
              <Navigator PaperProps={{ style: { width: drawerWidth } }} />
            </Hidden>
          </nav>
          <div className={classes.app}>
            <Switch>
              {/* Begin the views */}
              <Route path="/sources/upload">
                <Header onDrawerToggle={handleDrawerToggle} />
                <main className={classes.main}>
                  <SourcesUpload backend={backend} />
                </main>
              </Route>
              <Route path="/settings/backend">
                <Header onDrawerToggle={handleDrawerToggle} />
                <main className={classes.main}>
                  <SettingsBackend
                    backend={backend}
                    saveBackend={saveBackend}
                  />
                </main>
              </Route>
              {/* When URL path is / redirect to the default route */}
              <Route
                exact
                path="/"
                render={({ location }) => (
                  <Redirect
                    to={{
                      pathname: "/" + DEFAULT_VIEW_ROUTE,
                      state: { from: location }
                    }}
                  />
                )}
              />
              {/* 404 Handler */}
              <Route path="*">
                <Header onDrawerToggle={handleDrawerToggle} />
                <main className={classes.main}>
                  <NotFound />
                </main>
              </Route>
            </Switch>
            <footer className={classes.footer}>
            </footer>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}

Paperbase.propTypes = {
  classes: PropTypes.object.isRequired,
  demoServer: PropTypes.object.isRequired,
};

export default withStyles(styles)(Paperbase);
