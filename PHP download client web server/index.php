<?php
    include_once "login_first.htm";
    require_once("DBHandler.php");
    $db = new DBHandler();
    $regexExpression = '/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[;])\S{7,}$/';
    $outputUsernameArray = array();
    $outputPasswordArray = array();
    if (isset($_POST['username']) && isset($_POST['password'])) {
        if ((strlen(trim($_POST['username'])) > 0) && (strlen(trim($_POST['password'])) > 0)) {
            preg_match($regexExpression, $_POST['username'], $outputUsernameArray);
            preg_match($regexExpression, $_POST['password'], $outputPasswordArray);
            if (count($outputUsernameArray) != 0 && count($outputPasswordArray) != 0) {
                if ($db->login_check($_POST['username'], password_hash($_POST['password'], PASSWORD_BCRYPT, ["cost" => 8]))) {
                    $status = $db->permissionLevel($_POST['username']);	
                    if(file_exists('client0.zip') && $status == 0)
                        echo '<a href="client0.zip" download>PRESS ME TO DOWNLOAD</a>';
                    elseif(file_exists('client1.zip') && $status == 1)
                        echo '<a href="client1.zip" download>PRESS ME TO DOWNLOAD</a>';
                    elseif(file_exists('client2.zip') && $status == 2)
                        echo '<a href="client2.zip" download>PRESS ME TO DOWNLOAD</a>';
                    else
                        echo "Enternal error, file wasn't found, or server had been under attack.";
                }
                else
                    echo "Invalid input, insufficient permissions.";
            }
            else
                echo "Invalid input, wrong username or password format.";
        }
        else
            echo "Username or password weren't entered.<br>Please try again.";
    }
    $db = null;
    include_once "login_last.htm";
?>
