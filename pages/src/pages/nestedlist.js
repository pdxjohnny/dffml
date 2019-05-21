import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import ListSubheader from '@material-ui/core/ListSubheader';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';

const styles = theme => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
  nested: {
    paddingLeft: theme.spacing.unit * 4,
  },
});

class NestedList extends React.Component {
  state = {
    open: false,
  };

  expandList = () => {
    this.setState(state => ({ open: !state.open }));
  };

  render() {
    const { children, classes, title, selectedPath, canonical, data, onSelect } = this.props;
    const { open } = this.state;

    var subs = Object.keys(data)
               .filter(key => !key.startsWith('__'))
               .map((key, index) => (
                 <NestedList
                   key={key}
                   title={data[key].__canonical}
                   data={data[key]}
                   canonical={data[key].__canonical}
                   selectedPath={selectedPath}
                   onSelect={onSelect}
                   classes={classes} />
               ));

    if (subs.length > 0) {
      return (
        <React.Fragment>
          <ListItem button selected={selectedPath.startsWith(canonical)}>
            <ListItemText onClick={() => {onSelect(canonical)}} inset primary={title} />
            <div onClick={this.expandList}>
              {open ? <ExpandLess /> : <ExpandMore />}
            </div>
          </ListItem>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <List component="div">
              {subs}
            </List>
          </Collapse>
        </React.Fragment>
      );
    } else {
      return (
        <React.Fragment>
          <ListItem button selected={selectedPath.startsWith(canonical)}>
            <ListItemText onClick={() => {onSelect(canonical)}} inset primary={title} />
          </ListItem>
        </React.Fragment>
      );
    }
  }
}

NestedList.propTypes = {
  classes: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  canonical: PropTypes.string.isRequired,
  selectedPath: PropTypes.string.isRequired,
  onSelect: PropTypes.func.isRequired,
  data: PropTypes.object.isRequired,
};

export default withStyles(styles)(NestedList);
