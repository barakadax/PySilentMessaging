<?php
    class DBHandler {
        private $dbconn;
        private $result;
        private $numrows;

        public function login_check($username, $password) {
            $this->dbconn = pg_connect("host=localhost port=5432 dbname=postgres user=postgres password=1234");
            $this->result = pg_query("SELECT * FROM \"silentUsers\" WHERE \"Username\" = '$username'");
            $this->numrows = pg_numrows($this->result);
            if ($this->numrows != 1)
                return $this->disconnect(FALSE);
            $user = pg_fetch_array($this->result, 0, PGSQL_ASSOC);
            if (password_verify($user['Password'], $password))
                return $this->disconnect(TRUE);
            return $this->disconnect(FALSE);
        }  // O(1)
        
        public function permissionLevel($username) {
           $this->dbconn = pg_connect("host=localhost port=5432 dbname=postgres user=postgres password=1234");
           $this->result = pg_query("SELECT * FROM \"silentUsers\" WHERE \"Username\" = '$username'");
           if ($this->numrows != 1)
              return $this->disconnect(3);
           $user = pg_fetch_array($this->result, 0, PGSQL_ASSOC);
           return $this->disconnect($user['PermissionLevel']);
        }  // O()

        private function disconnect($returnValue) {
            pg_free_result($this->result);
            pg_close($this->dbconn);
            return $returnValue;
        }  //O(1)
    }
?>
