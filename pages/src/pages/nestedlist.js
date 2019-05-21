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
    selected: false,
  };

  selectItem = () => {
    this.props.onSelect(this.props.key);
    this.setState(state => ({ selected: true }));
  };

  expandList = () => {
    this.setState(state => ({ open: !state.open }));
  };

  render() {
    const { children, classes, title, resource } = this.props;
    const { open, selected } = this.state;

    return (
      <span>
        <ListItem button selected={selected}>
          <ListItemText onClick={this.selectItem} inset primary="Inbox" />
          <div onClick={this.expandList}>
            {open ? <ExpandLess /> : <ExpandMore />}
          </div>
        </ListItem>
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {children}
          </List>
        </Collapse>
      </span>
    );
  }
}

NestedList.propTypes = {
  classes: PropTypes.object.isRequired,
  resource: PropTypes.string.isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default withStyles(styles)(NestedList);
