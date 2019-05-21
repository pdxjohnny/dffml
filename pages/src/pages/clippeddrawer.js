import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import CssBaseline from '@material-ui/core/CssBaseline';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Collapse from '@material-ui/core/Collapse';
import ListItem from '@material-ui/core/ListItem';
import ListSubheader from '@material-ui/core/ListSubheader';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';
import { Route, Link } from "react-router-dom";

import NestedList from './nestedlist';

const drawerWidth = 240;

const styles = theme => ({
  root: {
    display: 'flex',
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing.unit * 3,
  },
  toolbar: theme.mixins.toolbar,
});

function Home() {
  return <h2>Home</h2>;
}

function About() {
  return <h2>About</h2>;
}

function Topic({ match }) {
  return <h3>Requested Param: {match.params.id}</h3>;
}

function Topics({ match }) {
  return (
    <div>
      <h2>Topics</h2>

      <ul>
        <li>
          <Link to={`${match.url}/components`}>Components</Link>
        </li>
        <li>
          <Link to={`${match.url}/props-v-state`}>Props v. State</Link>
        </li>
      </ul>

      <Route path={`${match.path}/:id`} component={Topic} />
      <Route
        exact
        path={match.path}
        render={() => <h3>Please select a topic.</h3>}
      />
    </div>
  );
}

function Header() {
  return (
    <ul>
      <li>
        <Link to="/">Home</Link>
      </li>
      <li>
        <Link to="/about">About</Link>
      </li>
      <li>
        <Link to="/topics">Topics</Link>
      </li>
    </ul>
  );
}

function FunctionDoc(props) {
  const { doc } = props;

  if (typeof doc.docstring !== 'string' ||
      doc.docstring === null) {
    doc.docstring = '';
  }

  return (
    <React.Fragment>
      <h4>{doc.name}{doc.args}</h4>
      <Typography paragraph>
      {doc.docstring.split('\n').map((line, index) => {
        return <span key={index}>{line}<br/></span>
      })}
      </Typography>
    </React.Fragment>
  );
}

function ClassDoc(props) {
  const { doc } = props;

  if (typeof doc.docstring !== 'string' ||
      doc.docstring === null) {
    doc.docstring = '';
  }

  return (
    <React.Fragment>
      <h3>{doc.name}</h3>
      <Typography paragraph>
      {doc.docstring.split('\n').map((line, index) => {
        return <span key={index}>{line}<br/></span>
      })}
      </Typography>
      {Object.keys(doc.methods).map((name, index) => {
        return <FunctionDoc key={index} doc={doc.methods[name]}></FunctionDoc>
      })}
    </React.Fragment>
  );
}

class ClippedDrawer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedPath: '',
    };
  }

  selectItem = (canonical) => {
    this.setState({ selectedPath: canonical });
  };

  render() {
    const { classes, title, data, onSelect } = this.props;
    const { selectedPath } = this.state;

    var display = <h1>DFFML API Documentation</h1>;

    if (selectedPath.length) {
      var current = data;
      var split = selectedPath.split('.');
      for (var i in split) {
        i = split[i];
        if (!current.hasOwnProperty(i)) {
          display = <h1>Documentation Not Found</h1>;
          break;
        }
        current = current[i];
      }
      display = (
        <React.Fragment>
          <h1>{current.__canonical}</h1>
          <p>{current.__filename}</p>
          {Object.keys(current.__classes)
           .map((key, index) => (
            <ClassDoc
              key={key}
              doc={current.__classes[key]} />
          ))}
        </React.Fragment>
      );
    }

    return (
      <div className={classes.root}>
        <CssBaseline />
        <AppBar position="fixed" className={classes.appBar}>
          <Toolbar>
            <Typography variant="h6" color="inherit" noWrap>
              {title}
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          className={classes.drawer}
          variant="permanent"
          classes={{
            paper: classes.drawerPaper,
          }}
        >
          <div className={classes.toolbar} />
          <List
            component="nav"
            subheader={<ListSubheader component="div">API Reference</ListSubheader>} >
            {Object.keys(data)
              .filter(key => !key.startsWith('__'))
              .map((key, index) => (
              <NestedList
                key={key}
                title={data[key].__canonical}
                data={data[key]}
                canonical={data[key].__canonical}
                selectedPath={selectedPath}
                onSelect={this.selectItem} />
            ))}
          </List>
          <Divider />
        </Drawer>
        <main className={classes.content}>
          <div className={classes.toolbar} />
          {display}
        </main>
      </div>
    );
  }
}

ClippedDrawer.propTypes = {
  classes: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  data: PropTypes.object.isRequired,
};

export default withStyles(styles)(ClippedDrawer);
