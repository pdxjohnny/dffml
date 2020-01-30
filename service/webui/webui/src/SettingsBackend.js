import React from 'react';
import PropTypes from 'prop-types';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
  paper: {
    maxWidth: 936,
    margin: 'auto',
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
  formText: {
    margin: '16px',
    width: "100%",
  },
  formButton: {
    margin: '26px',
  },
  formProgress: {
    margin: '22px',
  },
});


function Content(props) {
  const { classes, backend, saveBackend } = props;
  const [ backend_url, setBackend ] = React.useState(backend.url);

  console.log(backend_url, backend)

  return (
    <React.Fragment>
      <Paper className={classes.paper}>
        <Grid container spacing={3}>
          <Grid item xs={8}>
            <TextField className={classes.formText} name="backend_url" label="Backend URL" value={backend_url} onChange={(evt) => setBackend(evt.target.value)}/>
          </Grid>
          <Grid item xs={4}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => saveBackend(backend_url)}
              className={classes.formButton}
            >
              Submit
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </React.Fragment>
  );
}

Content.propTypes = {
  classes: PropTypes.object.isRequired,
  backend: PropTypes.object.isRequired,
  saveBackend: PropTypes.func.isRequired,
};

export default withStyles(styles)(Content);
