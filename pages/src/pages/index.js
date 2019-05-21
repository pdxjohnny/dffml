import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import withRoot from '../withRoot';

import ClippedDrawer from './clippeddrawer';

const style = theme => {};

class Dashboard extends React.Component {

  constructor() {
    super();
    this.state = {
      data: {}
    };
  }

  componentDidMount = () => {
    this.getData();
  };

  async getData () {
    try {
      var json = await (await fetch('docs.json')).json();
    } catch (err) {
      console.error(err);
      return;
    }

    this.setState({
      data: json
    });
  };

  async onSelect(key) {
    console.log(key)
  }

  render() {
    const { classes } = this.props;
    const { data } = this.state;

    console.log(data)

    return (
      <ClippedDrawer
          title={"DFFML Documentation"}
          classes={classes}
          data={data}
          onSelect={this.onSelect} />
    );
  }
}

export default withRoot(withStyles(style)(Dashboard));
