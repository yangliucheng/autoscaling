package db

import (
	"Stardigi-Policy/utils"
	"database/sql"
	"fmt"
	// "github.com/astaxie/beego/orm"
	_ "github.com/go-sql-driver/mysql"
	"time"
)

var (
	DBsqler = make(map[string]Sqler)
)

type DBclient struct {
	object  interface{}
	Db      chan *sql.DB
	StrChan chan string
}

func SetDBsqler(name string, sqler Sqler) {

	DBsqler[name] = sqler
}

func GetDBsqker(name string) Sqler {

	return DBsqler[name]
}

func NewDBClient(dbType, dataSourceName string) *DBclient {

	driverName := make(chan string, 1)
	timeout := make(chan int)
	errchan := make(chan error)
	dbChan := make(chan *sql.DB, 1)
	driverName <- dbType
	go func() {
		time.Sleep(time.Second * 10)
		timeout <- 1
	}()

	// 启动goroutine来执行sql注册
	go func(driverName chan string) {

		for {
			select {
			case dbType := <-driverName:
				switch dbType {
				case "mysql":
					db, err := sql.Open(dbType, dataSourceName)
					if err != nil {
						errchan <- err
					}

					dbChan <- db
				}
				return
			case err := <-errchan:
				fmt.Println("open mysql db fail,", err)
				return
			case <-timeout:
				fmt.Println("open mysql db timeout")
				return
			}
		}
	}(driverName)

	dbClient := &DBclient{
		Db: dbChan,
	}
	SetDBsqler(dbType, dbClient)
	return dbClient
}

func (dbClient *DBclient) Insert(object interface{}) {

	name := utils.NameParaseWithReflect(object)
	table := utils.StringParaseWith_(name)
	stat, value := utils.ParaseInterface(object)

	con := utils.StringJoin("INSERT INTO ", table, " SET ", stat)
	db := <-dbClient.Db
	stmt, err := db.Prepare(con)
	if err != nil {
		fmt.Println("插入数据看失败", err)
	}
	fmt.Println("======数据库=======", con, value)
	_, err = stmt.Exec(value...)
	if err != nil {
		fmt.Println("插入数据看失败", err)
	}
}

func (dbClient *DBclient) QueryTable(object interface{}) QuerySet {

	dbClient.StrChan = make(chan string, 1)

	name := utils.NameParaseWithReflect(object)
	table := utils.StringParaseWith_(name)

	str := utils.StringJoin("SELECT * from ", table)

	dbClient.StrChan <- str
	dbClient.object = object
	starQuerySet := NewStarQuerySet(dbClient)
	return starQuerySet
}

// const (
// 	// maximum connections of idle(optional)
// 	maxIdle int = 30
// 	// maxxium connections of connected(optional)
// 	maxConn int = 30
// )

// type Database struct {
// 	Finish     chan bool
// 	Type       string
// 	DataSource string
// }

// func NewDatabase() *Database {

// 	return &Database{}
// }

// func (db *Database) SetType(dbtype string) *Database {

// 	db.Type = dbtype
// 	return db
// }

// func (db *Database) SetDataSource(dataSource string) *Database {

// 	db.DataSource = dataSource
// 	return db
// }

// func (db *Database) SetFinish() *Database {

// 	finish := make(chan bool, 1)
// 	finish <- true
// 	db.Finish = finish
// 	return db
// }

// /**
//  * initialize database
//  */
// func (database *Database) InitDB() {
// 	fmt.Println("===InitDB===", database.Type)
// 	// set type of database
// 	dbType := make(chan string, 1)
// 	dbType <- database.Type

// 	fmt.Println("===begin===")
// 	// register database
// 	register(dbType, database.DataSource)
// 	fmt.Println("===register end===")
// 	// model register
// 	orm.RegisterModel(new(AppScaleRule))
// 	// param01 alias name of table
// 	// param02 forced to create table , table create when install our platment
// 	// param02 whether or not show info when create table,true->not show
// 	orm.RunSyncdb("default", false, false)
// 	// test()
// }
// func register(dbType chan string, dataSource string) {

// 	timeout := make(chan int)
// 	errchan := make(chan error)
// 	go func() {
// 		time.Sleep(time.Second * 10)
// 		timeout <- 1
// 	}()

// 	for {
// 		select {
// 		case dt := <-dbType:
// 			switch dt {
// 			case "mysql":
// 				fmt.Println("====mysql=====")
// 				// drive register
// 				err := orm.RegisterDriver(dt, orm.DRMySQL)
// 				if err != nil {
// 					errchan <- err
// 				}

// 				// datasource regsiter
// 				err = orm.RegisterDataBase("default", dt, dataSource, maxIdle, maxConn)
// 				if err != nil {
// 					errchan <- err
// 				}
// 				return
// 			}
// 		case errc := <-errchan:
// 			fmt.Println("register mysql err", errc)
// 			return
// 		case <-timeout:
// 			fmt.Println("register mysql timeout")
// 			return
// 		}
// 	}
// }
