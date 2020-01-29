import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

export default function SetBackendPopup(props) {
  const [open, setOpen] = React.useState(props.open);

  var backend_url = "";

  const handleCloseDemoMode = () => {
    props.saveBackend("demo");
    setOpen(false);
  };

  const handleCloseSave = () => {
    props.saveBackend(backend_url);
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={handleCloseDemoMode} aria-labelledby="form-dialog-title">
      <DialogTitle id="form-dialog-title">Set Backend</DialogTitle>
      <DialogContent>
        <DialogContentText>
          The web interface requires a backend server to be fully operational.
          Instructions on how to start the server can be found <a href="https://intel.github.io/dffml/plugins/service/http/index.html" >here</a>.
          If you only want to play around and get a feel for things, click
          "Demo Mode" instead of "Save".
        </DialogContentText>
        <TextField
          autoFocus
          margin="dense"
          label="URL Of Backend"
          type="url"
          onChange={evt => backend_url = (evt.target.value)}
          fullWidth
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCloseDemoMode} color="primary">
          Demo Mode
        </Button>
        <Button onClick={handleCloseSave} color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
