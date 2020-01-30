import React from 'react';
import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Grid from '@material-ui/core/Grid';
import HelpIcon from '@material-ui/icons/Help';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import { useRouteMatch } from "react-router-dom";

const lightColor = 'rgba(255, 255, 255, 0.7)';

const styles = theme => ({
  secondaryBar: {
    zIndex: 0,
  },
  toolbar: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  menuButton: {
    marginLeft: -theme.spacing(1),
  },
  iconButtonAvatar: {
    padding: 4,
  },
  link: {
    textDecoration: 'none',
    color: lightColor,
    '&:hover': {
      color: theme.palette.common.white,
    },
  },
  button: {
    borderColor: lightColor,
  },
});

const titles = {
  "/sources/upload": {
    title: "Files and Uploads",
    help: "https://intel.github.io/dffml/webui/help/for/sources",
  },
  "/sources/configure": {
    title: "Configure Data Sources",
    help: "https://intel.github.io/dffml/webui/help/for/sources",
  },
  "/sources/explore": {
    title: "Explore Data Sources",
    help: "https://intel.github.io/dffml/webui/help/for/sources",
  },
  "/settings/backend": {
    title: "Backend Settings",
    help: "https://intel.github.io/dffml/webui/help/for/backend",
  },
};

function Header(props) {
  const { classes } = props;

  let match = useRouteMatch();

  var title = "Not Found";

  if (titles.hasOwnProperty(match.path)) {
    title = titles[match.path].title;
  }

  return (
    <React.Fragment>
      <AppBar
        component="div"
        className={classes.secondaryBar}
        color="primary"
        position="static"
        elevation={0}
      >
        <Toolbar className={classes.toolbar}>
          <Grid container alignItems="center" spacing={1}>
            <Grid item xs>
              <Typography color="inherit" variant="h5" component="h1">
                {title}
              </Typography>
            </Grid>
            <Grid item>
              <Tooltip title="Help">
                <IconButton color="inherit">
                  {/* TODO Use help links with HelpIcon / IconButton */}
                  <HelpIcon />
                </IconButton>
              </Tooltip>
            </Grid>
          </Grid>
        </Toolbar>
      </AppBar>
    </React.Fragment>
  );
}

Header.propTypes = {
  classes: PropTypes.object.isRequired,
  onDrawerToggle: PropTypes.func.isRequired,
};

export default withStyles(styles)(Header);
